# 역할: 테스트 실패 시 Jira 티켓 자동 생성 및 댓글 추가

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

UNITY_VERSION = os.getenv("UNITY_VERSION", "6000.3.8f1")

# 다른 프로젝트 티켓과 구분하기 위한 접두어
TICKET_PREFIX = "[FAIL][Unity]"

ISSUE_TYPE = "버그"

TEST_TARGET = "Sentaur Survivors (Unity PlayMode)"


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

    def __init__(self):
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

    def _build_description(self, test_id, test_name, message, stack_trace):
        """
        티켓 본문 조립.

        batchmode 실행이라 스크린샷 첨부가 불가능하므로
        NUnit 이 제공하는 stack trace 로 대체한다.
        """
        return (
            f"## 실행 환경\n"
            f"- OS: {platform.system()} {platform.release()}\n"
            f"- Python: {sys.version.split()[0]}\n"
            f"- Unity: {UNITY_VERSION}\n"
            f"- 테스트 대상: {TEST_TARGET}\n"
            f"- 실행 모드: batchmode (CI)\n"
            f"\n"
            f"## 실패한 테스트\n"
            f"- ID: {test_id}\n"
            f"- 이름: {test_name}\n"
            f"\n"
            f"## 실패 메시지\n"
            f"{message}\n"
            f"\n"
            f"## Stack Trace\n"
            f"{stack_trace}\n"
            f"\n"
            f"## 실패 시각\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def report_failure(self, test_id, test_name, message, stack_trace):
        """실패 보고. 기존 티켓 있으면 댓글, 없으면 신규 생성."""
        summary = f"{TICKET_PREFIX} {test_id} {test_name}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        issue_key = self._search_issue(summary)

        if issue_key:
            comment = (
                f"재실패 발생\n\n"
                f"시각: {timestamp}\n"
                f"메시지: {message}\n\n"
                f"Stack Trace:\n{stack_trace}"
            )
            self._add_comment(issue_key, comment)
            print(f"[Jira] 기존 티켓 {issue_key} 에 댓글 추가")
        else:
            description = self._build_description(test_id, test_name, message, stack_trace)
            issue_key = self._create_issue(summary, description)

            if issue_key is None:
                print("[Jira] 티켓 생성 실패")
                return None

            print(f"[Jira] 새 티켓 {issue_key} 생성")

        return issue_key