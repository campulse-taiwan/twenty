#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch translate zh-TW.po files from English msgid entries."""

import re
import sys
import time
from pathlib import Path

import polib
from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent.parent

PO_FILES = [
    ROOT / "packages/twenty-emails/src/locales/zh-TW.po",
    ROOT / "packages/twenty-front/src/locales/zh-TW.po",
    ROOT / "packages/twenty-server/src/engine/core-modules/i18n/locales/zh-TW.po",
]

KEEP_ENGLISH_PATTERN = re.compile(
    r"\b(?:"
    r"Twenty|GitHub|Github|OAuth|SSO|API|MCP|CSV|URL|URI|HTTP|HTTPS|SAML|ACS|"
    r"IMAP|SMTP|ActiveSync|npm|ClickHouse|OpenAI|ANTHROPIC|XAI|AKIA|Claude|Cursor|"
    r"Windsurf|Cline|Zed|Google|Microsoft|San Francisco|Paris|CRM|SSL|TLS|DNS|"
    r"IP|PDF|JSON|XML|HTML|CSS|SDK|CLI|SSH|VPN|GDPR|In-Reply-To|Enterprise|OK|ms"
    r")\b",
    re.IGNORECASE,
)

ENGLISH_WORD = re.compile(r"[A-Za-z]{3,}")

ICU_BRANCH_KEYWORD_RE = re.compile(
    r"(?P<keyword>zero|one|two|few|many|other|=\d+|\w+)",
    re.IGNORECASE,
)

ICU_PLURAL_RE = re.compile(
    r"\{(?P<var>[^,{}]+),\s*plural\s*,\s*(?P<branches>.+)\}$",
    re.IGNORECASE,
)

ICU_SELECT_RE = re.compile(
    r"\{(?P<var>[^,{}]+),\s*select\s*,\s*(?P<branches>.+)\}$",
    re.IGNORECASE,
)

ICU_SELECTORDINAL_RE = re.compile(
    r"\{(?P<var>[^,{}]+),\s*selectordinal\s*,\s*(?P<branches>.+)\}$",
    re.IGNORECASE,
)


def protect_simple_placeholders(text: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def save(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"XPHX{len(protected) - 1}XPHX"

    text = re.sub(r"<\d+>.*?</\d+>", save, text, flags=re.DOTALL)
    text = re.sub(r"<\d+/>", save, text)
    text = re.sub(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}", save, text)
    text = re.sub(r"\{\d+\}", save, text)
    text = re.sub(r"\{#[^}]*\}", save, text)
    text = text.replace("{#", "XHASHX")
    return text, protected


def restore_simple_placeholders(text: str, protected: list[str]) -> str:
    text = text.replace("XHASHX", "{#")
    for index, value in enumerate(protected):
        text = text.replace(f"XPHX{index}XPHX", value)
    return text


def translate_plain_text(translator: GoogleTranslator, text: str) -> str:
    protected_text, protected = protect_simple_placeholders(text)
    translated = translator.translate(protected_text)
    if not translated:
        raise ValueError("empty translation")
    return restore_simple_placeholders(translated, protected)


def extract_icu_branches(branches_text: str) -> list[tuple[str, str]]:
    branches: list[tuple[str, str]] = []
    index = 0

    while index < len(branches_text):
        while index < len(branches_text) and branches_text[index].isspace():
            index += 1

        keyword_match = ICU_BRANCH_KEYWORD_RE.match(branches_text, index)
        if not keyword_match:
            break

        keyword = keyword_match.group("keyword")
        index = keyword_match.end()

        while index < len(branches_text) and branches_text[index].isspace():
            index += 1

        if index >= len(branches_text) or branches_text[index] != "{":
            break

        depth = 0
        content_start = index + 1
        while index < len(branches_text):
            if branches_text[index] == "{":
                depth += 1
            elif branches_text[index] == "}":
                depth -= 1
                if depth == 0:
                    content = branches_text[content_start:index]
                    branches.append((keyword, content))
                    index += 1
                    break
            index += 1
        else:
            break

    return branches


def translate_branch_content(
    translator: GoogleTranslator,
    content: str,
) -> str:
    if not content.strip():
        return content

    stripped = content.strip()
    if re.fullmatch(r"#\w*", stripped):
        suffix = stripped[1:]
        if suffix:
            return f"#{translate_plain_text(translator, suffix)}"
        return content

    if stripped.startswith("#"):
        remainder = stripped[1:].lstrip()
        translated = translate_plain_text(translator, remainder)
        return f"# {translated}".rstrip()

    return translate_plain_text(translator, content)


def translate_icu_message(
    translator: GoogleTranslator,
    match: re.Match[str],
    message_type: str,
) -> str:
    variable = match.group("var").strip()
    branches_text = match.group("branches")
    translated_branches: list[str] = []

    for keyword, content in extract_icu_branches(branches_text):
        translated_content = translate_branch_content(translator, content)
        translated_branches.append(f"{keyword} {{{translated_content}}}")

    return f"{{{variable}, {message_type}, {' '.join(translated_branches)}}}"


def translate_text(translator: GoogleTranslator, text: str, retries: int = 3) -> str:
    if text in {"—", "#", "-"}:
        return text

    for attempt in range(retries):
        try:
            if ICU_SELECTORDINAL_RE.fullmatch(text):
                return ICU_SELECTORDINAL_RE.sub(
                    lambda match: translate_icu_message(
                        translator, match, "selectordinal"
                    ),
                    text,
                )

            if ICU_SELECT_RE.fullmatch(text):
                return ICU_SELECT_RE.sub(
                    lambda match: translate_icu_message(translator, match, "select"),
                    text,
                )

            if ICU_PLURAL_RE.fullmatch(text):
                return ICU_PLURAL_RE.sub(
                    lambda match: translate_icu_message(translator, match, "plural"),
                    text,
                )

            return translate_plain_text(translator, text)
        except Exception as error:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))

    return text


def has_translatable_english(text: str) -> bool:
    if not text:
        return False
    stripped = KEEP_ENGLISH_PATTERN.sub("", text)
    return bool(ENGLISH_WORD.search(stripped))


def needs_translation(entry: polib.POEntry) -> bool:
    if not entry.msgid:
        return False
    if not entry.msgstr:
        return True
    if entry.msgstr == entry.msgid:
        return True
    if has_translatable_english(entry.msgstr):
        return True
    return False


def process_po_file(po_path: Path, translator: GoogleTranslator) -> tuple[int, int]:
    po = polib.pofile(str(po_path))
    translated_count = 0
    skipped_count = 0

    for entry in po:
        if not entry.msgid or not needs_translation(entry):
            continue

        try:
            entry.msgstr = translate_text(translator, entry.msgid)
            translated_count += 1
            if translated_count % 50 == 0:
                print(
                    f"  [{po_path.name}] {translated_count} translated, saving...",
                    flush=True,
                )
                po.save(str(po_path))
            time.sleep(0.12)
        except Exception as error:  # noqa: BLE001
            skipped_count += 1
            print(f"  SKIP: {entry.msgid[:70]!r} -> {error}", file=sys.stderr)

    po.save(str(po_path))
    print(f"Done {po_path}: translated={translated_count}, skipped={skipped_count}")
    return translated_count, skipped_count


def main() -> None:
    translator = GoogleTranslator(source="en", target="zh-TW")
    grand_translated = 0
    grand_skipped = 0

    for po_path in PO_FILES:
        print(f"Processing {po_path}...")
        translated, skipped = process_po_file(po_path, translator)
        grand_translated += translated
        grand_skipped += skipped

    print(f"\nAll done: translated={grand_translated}, skipped={grand_skipped}")


if __name__ == "__main__":
    main()
