import polib
import re

EN = re.compile(r"[A-Za-z]{3,}")
KEEP = re.compile(
    r"Twenty|GitHub|OAuth|API|SSO|CSV|URL|CRM|Github|MCP", re.IGNORECASE
)


def stats(path: str) -> None:
    po = polib.pofile(path)
    total = empty = same = english = 0
    for entry in po:
        if not entry.msgid:
            continue
        total += 1
        if not entry.msgstr:
            empty += 1
        elif entry.msgstr == entry.msgid:
            same += 1
        elif EN.search(KEEP.sub("", entry.msgstr)):
            english += 1
    done = total - empty - same
    print(
        f"{path}: done={done}/{total} ({done / total * 100:.1f}%), "
        f"empty={empty}, same={same}, en_fragments={english}"
    )


for file_path in [
    "packages/twenty-emails/src/locales/zh-TW.po",
    "packages/twenty-front/src/locales/zh-TW.po",
    "packages/twenty-server/src/engine/core-modules/i18n/locales/zh-TW.po",
]:
    stats(file_path)
