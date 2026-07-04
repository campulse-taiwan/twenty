#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate zh-TW command menu label translations for the frontend."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONSTANT_FILE = (
    ROOT
    / "packages/twenty-server/src/engine/workspace-manager/twenty-standard-application/constants/standard-command-menu-item.constant.ts"
)
OUTPUT_FILE = (
    ROOT
    / "packages/twenty-front/src/modules/command-menu-item/utils/command-menu-item-label-translations.zh-TW.ts"
)

LABEL_RE = re.compile(
    r"(?:label|shortLabel):\s*(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")"
)

MANUAL_TRANSLATIONS: dict[str, str] = {
    "Navigate to next ${capitalize(objectMetadataItem.labelSingular)}": "前往下一筆 ${capitalize(objectMetadataItem.labelSingular)}",
    "Navigate to previous ${capitalize(objectMetadataItem.labelSingular)}": "前往上一筆 ${capitalize(objectMetadataItem.labelSingular)}",
    "Create new ${capitalize(objectMetadataItem.labelSingular)}": "建立新 ${capitalize(objectMetadataItem.labelSingular)}",
    "Delete ${capitalize(objectMetadataLabel)}": "刪除 ${capitalize(objectMetadataLabel)}",
    "Restore ${capitalize(objectMetadataLabel)}": "還原 ${capitalize(objectMetadataLabel)}",
    "Permanently destroy ${capitalize(objectMetadataLabel)}": "永久刪除 ${capitalize(objectMetadataLabel)}",
    "Add to Favorites": "加入我的最愛",
    "Remove from Favorites": "從我的最愛移除",
    "Export to PDF": "匯出為 PDF",
    "Export ${capitalize(objectMetadataLabel)}": "匯出 ${capitalize(objectMetadataLabel)}",
    "Update ${capitalize(objectMetadataItem.labelPlural)}": "更新 ${capitalize(objectMetadataItem.labelPlural)}",
    "Merge ${capitalize(objectMetadataItem.labelPlural)}": "合併 ${capitalize(objectMetadataItem.labelPlural)}",
    "Import ${capitalize(objectMetadataItem.labelPlural)}": "匯入 ${capitalize(objectMetadataItem.labelPlural)}",
    "Export View": "匯出檢視",
    "See deleted ${capitalize(objectMetadataItem.labelPlural)}": "查看已刪除的 ${capitalize(objectMetadataItem.labelPlural)}",
    "Create View": "建立檢視",
    "Hide deleted ${capitalize(objectMetadataItem.labelPlural)}": "隱藏已刪除的 ${capitalize(objectMetadataItem.labelPlural)}",
    "Edit Layout": "編輯版面配置",
    "Edit Dashboard": "編輯儀表板",
    "Save Dashboard": "儲存儀表板",
    "Cancel Edition": "取消編輯",
    "Duplicate Dashboard": "複製儀表板",
    "Activate Workflow": "啟用工作流程",
    "Deactivate Workflow": "停用工作流程",
    "Discard Draft": "捨棄草稿",
    "Test Workflow": "測試工作流程",
    "See Active Version": "查看使用中版本",
    "See Runs": "查看執行紀錄",
    "See Versions History": "查看版本紀錄",
    "Add a Node": "新增節點",
    "Tidy up Workflow": "整理工作流程",
    "Duplicate Workflow": "複製工作流程",
    "See Version": "查看版本",
    "See Workflow": "查看工作流程",
    "Stop": "停止",
    "Retry": "重試",
    "Use as Draft": "設為草稿",
    "Search": "搜尋",
    "Ask AI": "詢問 AI",
    "View Previous AI Chats": "查看先前的 AI 對話",
    "Reply": "回覆",
    "Compose Email": "撰寫電子郵件",
    "Compose Campaign": "撰寫行銷郵件",
    "Go to Settings": "前往設定",
    "Go to Experience Settings": "前往體驗設定",
    "Go to Accounts Settings": "前往帳戶設定",
    "Go to Emails Settings": "前往電子郵件設定",
    "Go to Calendars Settings": "前往行事曆設定",
    "Go to General Settings": "前往一般設定",
    "Go to Data Model Settings": "前往資料模型設定",
    "Go to Members Settings": "前往成員設定",
    "Go to Roles Settings": "前往角色設定",
    "Go to Domains Settings": "前往網域設定",
    "Go to Billing Settings": "前往帳單設定",
    "Go to APIs & Webhooks Settings": "前往 API 與 Webhook 設定",
    "Go to Apps Settings": "前往應用程式設定",
    "Go to AI Settings": "前往 AI 設定",
    "Go to Security Settings": "前往安全設定",
    "Go to Admin Panel Settings": "前往管理面板設定",
    "Go to Community Settings": "前往社群設定",
    "Send Email": "傳送電子郵件",
    "New ${capitalize(objectMetadataItem.labelSingular)}": "新增 ${capitalize(objectMetadataItem.labelSingular)}",
    "Delete": "刪除",
    "Restore": "還原",
    "Destroy": "永久刪除",
    "Export": "匯出",
    "Update": "更新",
    "Merge": "合併",
    "Import": "匯入",
    "Deleted ${capitalize(objectMetadataItem.labelPlural)}": "已刪除的 ${capitalize(objectMetadataItem.labelPlural)}",
    "Hide deleted": "隱藏已刪除",
    "Edit": "編輯",
    "Save": "儲存",
    "Cancel": "取消",
    "Duplicate": "複製",
    "Activate": "啟用",
    "Deactivate": "停用",
    "Test": "測試",
    "See Versions": "查看版本",
    "Tidy up": "整理",
    "Previous AI Chats": "先前的 AI 對話",
    "Compose": "撰寫",
    "Campaign": "行銷郵件",
    "Settings": "設定",
    "Experience": "體驗",
    "Accounts": "帳戶",
    "Emails": "電子郵件",
    "Calendars": "行事曆",
    "General": "一般",
    "Data Model": "資料模型",
    "Members": "成員",
    "Roles": "角色",
    "Domains": "網域",
    "Billing": "帳單",
    "APIs & Webhooks": "API 與 Webhook",
    "Apps": "應用程式",
    "AI": "AI",
    "Security": "安全",
    "Admin Panel": "管理面板",
    "Community": "社群",
}


def extract_labels() -> list[str]:
    content = CONSTANT_FILE.read_text(encoding="utf-8")
    labels: set[str] = set()

    for match in LABEL_RE.finditer(content):
        label = match.group(1) or match.group(2)
        if label:
            labels.add(label)

    return sorted(labels)


def escape_ts_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("`", "\\`")


def generate_file(labels: list[str]) -> None:
    lines = [
        "// Generated by scripts/sync-command-menu-labels-zh-tw.py",
        "// Do not edit manually — re-run the script after changing standard command menu labels.",
        "",
        "export const COMMAND_MENU_ITEM_LABEL_TRANSLATIONS_ZH_TW: Record<string, string> = {",
    ]

    for label in labels:
        translation = MANUAL_TRANSLATIONS.get(label, label)
        lines.append(f"  `{escape_ts_string(label)}`: `{escape_ts_string(translation)}`,")

    lines.extend(["};", ""])
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    labels = extract_labels()
    generate_file(labels)
    print(f"Generated {OUTPUT_FILE} with {len(labels)} labels")


if __name__ == "__main__":
    main()
