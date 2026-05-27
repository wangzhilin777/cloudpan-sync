from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from cloudpan_sync import webapp
from cloudpan_sync.i18n import MESSAGES, messages_for


def main() -> None:
    app = webapp.create_app()
    client = TestClient(app)
    index_html = client.get("/").text
    app_js = client.get("/assets/app.js").text

    zh_payload = client.get("/api/i18n?lang=zh-CN").json()
    en_payload = client.get("/api/i18n?lang=en-US").json()
    fallback_payload = client.get("/api/i18n?lang=invalid-lang").json()

    zh_messages = dict(zh_payload.get("messages") or {})
    en_messages = dict(en_payload.get("messages") or {})
    fallback_messages = dict(fallback_payload.get("messages") or {})

    print(
        json.dumps(
            {
                "htmlHasLangSelector": 'id="langSelect"' in index_html,
                "htmlHasZhOption": '<option value="zh-CN">中文</option>' in index_html,
                "htmlHasEnOption": '<option value="en-US">English</option>' in index_html,
                "htmlStartsZhCn": '<html lang="zh-CN">' in index_html,
                "apiZhReturnsLang": zh_payload.get("lang") == "zh-CN",
                "apiEnReturnsLang": en_payload.get("lang") == "en-US",
                "apiFallbackReturnsZhCn": fallback_payload.get("lang") == "zh-CN",
                "messagesForFallbackUsesZhCn": messages_for("invalid-lang") == MESSAGES["zh-CN"],
                "apiZhHasCoreMessages": (
                    zh_messages.get("nav.pending") == "待处理"
                    and zh_messages.get("panel.new_task.title") == "新建任务向导"
                    and zh_messages.get("wizard.step.1") == "选择来源网盘"
                ),
                "apiEnHasCoreMessages": (
                    en_messages.get("nav.pending") == "Pending"
                    and en_messages.get("panel.new_task.title") == "New Task Wizard"
                    and en_messages.get("wizard.step.1") == "Choose source provider"
                ),
                "apiFallbackUsesZhMessages": (
                    fallback_messages.get("nav.pending") == "待处理"
                    and fallback_messages.get("panel.new_task.title") == "新建任务向导"
                ),
                "jsTracksLangState": 'lang: "zh-CN"' in app_js and "messages: {}" in app_js,
                "jsHasI18nLoader": 'async function loadI18n(lang)' in app_js and 'fetchJson(`/api/i18n?lang=${encodeURIComponent(lang)}`)' in app_js,
                "jsUpdatesDocumentLang": "document.documentElement.lang = state.lang;" in app_js,
                "jsUpdatesLangSelect": 'document.getElementById("langSelect").value = state.lang;' in app_js,
                "jsBindsLangChange": 'const langSelect = document.getElementById("langSelect");' in app_js
                and 'langSelect.addEventListener("change", async () => {' in app_js
                and "await loadI18n(langSelect.value);" in app_js,
                "jsUsesTranslatedNavAndWizardText": (
                    'document.getElementById("newTaskTitle").textContent = t("panel.new_task.title");' in app_js
                    and 'document.getElementById("newTaskSubtitle").textContent = t("panel.new_task.subtitle");' in app_js
                    and 'document.getElementById("wizardSecondaryTitle").textContent = t("panel.new_task.secondary");' in app_js
                    and 'document.getElementById("wizardSummaryTitle").textContent = t("panel.new_task.summary");' in app_js
                    and "for (const key of tabKeys)" in app_js
                    and "node.textContent = t(key);" in app_js
                    and "stepNode.textContent = `${index + 1}. ${t(step.title)}`;" in app_js
                    and "navNode.textContent = t(step.title);" in app_js
                    and "summaryBody.textContent = t(wizardSteps[state.activeWizardStep].description);" in app_js
                ),
                "i18nLanguageSwitchFlowMatchesExpectedMessages": (
                    'id="langSelect"' in index_html
                    and '<option value="zh-CN">中文</option>' in index_html
                    and '<option value="en-US">English</option>' in index_html
                    and '<html lang="zh-CN">' in index_html
                    and zh_payload.get("lang") == "zh-CN"
                    and en_payload.get("lang") == "en-US"
                    and fallback_payload.get("lang") == "zh-CN"
                    and messages_for("invalid-lang") == MESSAGES["zh-CN"]
                    and zh_messages.get("nav.pending") == "待处理"
                    and zh_messages.get("panel.new_task.title") == "新建任务向导"
                    and zh_messages.get("wizard.step.1") == "选择来源网盘"
                    and en_messages.get("nav.pending") == "Pending"
                    and en_messages.get("panel.new_task.title") == "New Task Wizard"
                    and en_messages.get("wizard.step.1") == "Choose source provider"
                    and fallback_messages.get("nav.pending") == "待处理"
                    and fallback_messages.get("panel.new_task.title") == "新建任务向导"
                    and 'lang: "zh-CN"' in app_js
                    and "messages: {}" in app_js
                    and 'async function loadI18n(lang)' in app_js
                    and 'fetchJson(`/api/i18n?lang=${encodeURIComponent(lang)}`)' in app_js
                    and "document.documentElement.lang = state.lang;" in app_js
                    and 'document.getElementById("langSelect").value = state.lang;' in app_js
                    and 'const langSelect = document.getElementById("langSelect");' in app_js
                    and 'langSelect.addEventListener("change", async () => {' in app_js
                    and "await loadI18n(langSelect.value);" in app_js
                    and 'document.getElementById("newTaskTitle").textContent = t("panel.new_task.title");' in app_js
                    and 'document.getElementById("newTaskSubtitle").textContent = t("panel.new_task.subtitle");' in app_js
                    and 'document.getElementById("wizardSecondaryTitle").textContent = t("panel.new_task.secondary");' in app_js
                    and 'document.getElementById("wizardSummaryTitle").textContent = t("panel.new_task.summary");' in app_js
                    and "for (const key of tabKeys)" in app_js
                    and "node.textContent = t(key);" in app_js
                    and "stepNode.textContent = `${index + 1}. ${t(step.title)}`;" in app_js
                    and "navNode.textContent = t(step.title);" in app_js
                    and "summaryBody.textContent = t(wizardSteps[state.activeWizardStep].description);" in app_js
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
