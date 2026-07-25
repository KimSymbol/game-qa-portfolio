# 역할: 테스트 실패 시 Jira 티켓 자동 생성 및 댓글 추가

import io
import json
import os
import platform
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


# ── 1. 변수 선언부 ──────────────────────────────────

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# 티켓 제목 접두어 - Flare RPG 등 다른 프로젝트 티켓과 구분
TICKET_PREFIX = "[FAIL][2048]"

ISSUE_TYPE = "버그"


# ── 2. 함수 선언부 ──────────────────────────────────

def _to_adf(text):
    """일반 텍스트를 Jira API v3 가 요구하는 ADF 형식으로 변환."""
    paragraphs = [
        {"type": "paragraph", "content": [{"type": "text", "text": line or " "}]}
        for line in text.split("\n")
    ]
    return {"type": "doc", "version": 1, "content": paragraphs}


class JiraReporter:
    """Jira REST API v3 연동 - 실패 시 티켓 생성 또는 댓글 추가."""

    def __init__(self, device=None):
        """device: uiautomator2 객체. 스크린샷 첨부와 환경 정보 수집에 사용."""
        self.device = device
        self.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def _search_issue(self, summary):
        """제목으로 기존 티켓 검색. 없으면 None 반환."""
        jql = f'project = {JIRA_PROJECT_KEY} AND summary ~ "\\"{summary}\\""'
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/search/jql",
            data=json.dumps({"jql": jql, "fields": ["summary"]}),
            headers=self.headers,
            auth=self.auth,
        )
        if response.status_code != 200:
            return None
        issues = response.json().get("issues", [])
        return issues[0]["key"] if issues else None

    def _create_issue(self, summary, description):
        """새 티켓 생성 후 이슈 키 반환."""
        payload = json.dumps({
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": summary,
                "description": _to_adf(description),
                "issuetype": {"name": ISSUE_TYPE},
            }
        })
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/issue",
            data=payload,
            headers=self.headers,
            auth=self.auth,
        )
        return response.json()["key"] if response.status_code == 201 else None

    def _add_comment(self, issue_key, comment):
        """기존 티켓에 댓글 추가."""
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment",
            data=json.dumps({"body": _to_adf(comment)}),
            headers=self.headers,
            auth=self.auth,
        )
        return response.status_code == 201

    def _attach_screenshot(self, issue_key, filename):
        """현재 기기 화면을 캡처해 티켓에 첨부."""
        if self.device is None:
            return False

        buffer = io.BytesIO()
        self.device.screenshot().save(buffer, format="PNG")

        # X-Atlassian-Token: no-check 는 Jira 첨부 API 필수 헤더 (CSRF 우회)
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/issue/{issue_key}/attachments",
            headers={"X-Atlassian-Token": "no-check"},
            auth=self.auth,
            files={"file": (filename, buffer.getvalue(), "image/png")},
        )
        return response.status_code == 200

    def _device_info(self):
        """테스트 대상 기기 정보 문자열 반환."""
        if self.device is None:
            return "- 기기: 정보 없음"

        info = self.device.device_info
        return (
            f"- 기기: {info['model']} ({info['serial']})\n"
            f"- Android: {info['version']}"
        )

    def _build_description(self, test_id, test_name, error_short, error_full):
        """티켓 본문 조립."""
        return (
            f"## 실행 환경\n"
            f"- 실행 OS: {platform.system()} {platform.release()}\n"
            f"- Python: {sys.version.split()[0]}\n"
            f"{self._device_info()}\n"
            f"- 앱: Privacy Friendly 2048\n"
            f"\n"
            f"## 실패한 테스트\n"
            f"- ID: {test_id}\n"
            f"- 이름: {test_name}\n"
            f"\n"
            f"## 에러 메시지\n"
            f"{error_short}\n"
            f"\n"
            f"## Traceback\n"
            f"{error_full}\n"
            f"\n"
            f"## 실패 시각\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def report_failure(self, test_id, test_name, error_short, error_full):
        """실패 보고. 기존 티켓 있으면 댓글, 없으면 신규 생성."""
        summary = f"{TICKET_PREFIX} {test_id} {test_name}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        issue_key = self._search_issue(summary)

        if issue_key:
            comment = (
                f"재실패 발생\n\n"
                f"시각: {timestamp}\n"
                f"에러: {error_short}\n\n"
                f"Traceback:\n{error_full}"
            )
            self._add_comment(issue_key, comment)
            print(f"[Jira] 기존 티켓 {issue_key} 에 댓글 추가")
        else:
            description = self._build_description(test_id, test_name, error_short, error_full)
            issue_key = self._create_issue(summary, description)
            if issue_key is None:
                print("[Jira] 티켓 생성 실패")
                return None
            print(f"[Jira] 새 티켓 {issue_key} 생성")

        filename = f"{test_id}_{timestamp.replace(':', '-').replace(' ', '_')}.png"
        if self._attach_screenshot(issue_key, filename):
            print("[Jira] 스크린샷 첨부 완료")

        return issue_key