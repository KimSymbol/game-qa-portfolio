# 역할: 테스트 실패 시 Jira 티켓 자동 생성 및 댓글 추가
# - 같은 제목의 티켓이 있으면 댓글 추가
# - 없으면 새 티켓 생성
# - 두 경우 모두 스크린샷 첨부

import os
import json
import platform
import sys
from datetime import datetime
import requests
import cv2
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from utils.screen_utils import capture_game

# .env 파일 로드 (JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY)
load_dotenv()


class JiraReporter:
    """
    Jira REST API v3 연동 클래스
    테스트 실패 시 자동으로 티켓 생성 또는 댓글 추가
    """

    def __init__(self):
        """환경변수에서 Jira 설정 로드"""
        self.url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")
        self.auth = HTTPBasicAuth(self.email, self.token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _search_issue(self, summary):
        """
        제목으로 이슈 검색
        JQL(Jira Query Language) 사용

        매개변수:
        - summary: 검색할 제목

        반환값:
        - 이슈 키 (예: "KAN-1") 또는 None
        """
        # 정확한 제목 매칭을 위해 따옴표로 감쌈
        jql = f'project = {self.project_key} AND summary ~ "\\"{summary}\\""'
        url = f"{self.url}/rest/api/3/search/jql"
        payload = json.dumps({"jql": jql, "fields": ["summary"]})

        response = requests.post(url, data=payload, headers=self.headers, auth=self.auth)
        if response.status_code == 200:
            issues = response.json().get("issues", [])
            return issues[0]["key"] if issues else None
        return None

    def _create_issue(self, summary, description):
        """
        새 이슈 생성

        매개변수:
        - summary: 티켓 제목
        - description: 티켓 본문 (마크다운 텍스트)

        반환값:
        - 생성된 이슈 키 또는 None
        """
        url = f"{self.url}/rest/api/3/issue"
        payload = json.dumps({
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                # Atlassian Document Format (ADF) - Jira 본문 형식
                "description": self._to_adf(description),
                "issuetype": {"name": "버그"}
            }
        })

        response = requests.post(url, data=payload, headers=self.headers, auth=self.auth)
        if response.status_code == 201:
            return response.json()["key"]
        return None

    def _add_comment(self, issue_key, comment):
        """
        이슈에 댓글 추가

        매개변수:
        - issue_key: 이슈 키 (예: "KAN-1")
        - comment: 댓글 내용
        """
        url = f"{self.url}/rest/api/3/issue/{issue_key}/comment"
        payload = json.dumps({"body": self._to_adf(comment)})

        response = requests.post(url, data=payload, headers=self.headers, auth=self.auth)
        return response.status_code == 201

    def _attach_screenshot(self, issue_key, filename="screenshot.png"):
        """
        현재 게임 화면을 캡처해서 이슈에 첨부

        매개변수:
        - issue_key: 이슈 키
        - filename: 첨부할 파일명
        """
        # 게임 화면 캡처
        screen = capture_game()
        _, buf = cv2.imencode(".png", screen)
        image_bytes = buf.tobytes()

        url = f"{self.url}/rest/api/3/issue/{issue_key}/attachments"
        # X-Atlassian-Token: no-check → Jira CSRF 우회 필수 헤더
        headers = {"X-Atlassian-Token": "no-check"}
        files = {"file": (filename, image_bytes, "image/png")}

        response = requests.post(url, headers=headers, auth=self.auth, files=files)
        return response.status_code == 200

    def _to_adf(self, text):
        """
        일반 텍스트를 Atlassian Document Format (ADF) 으로 변환
        Jira API v3 는 본문/댓글 모두 ADF 형식 요구

        매개변수:
        - text: 변환할 텍스트 (줄바꿈 \n 지원)
        """
        # 줄바꿈을 paragraph 로 분리
        paragraphs = []
        for line in text.split("\n"):
            paragraphs.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line if line else " "}]
            })
        return {"type": "doc", "version": 1, "content": paragraphs}

    def _build_description(self, test_id, test_name, error_short, error_full):
        """
        티켓 본문 생성

        매개변수:
        - test_id: 테스트 ID (예: "FR-008")
        - test_name: 테스트 이름
        - error_short: 짧은 에러 메시지 (AssertionError 메시지)
        - error_full: traceback 전체
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"## 실행 환경\n"
            f"- OS: {platform.system()} {platform.release()}\n"
            f"- Python: {sys.version.split()[0]}\n"
            f"- 게임: Flare RPG v1.15\n"
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
            f"{timestamp}"
        )

    def report_failure(self, test_id, test_name, error_short, error_full):
        """
        테스트 실패 시 호출하는 메인 메서드
        - 같은 제목 티켓이 있으면 → 댓글 + 스크린샷 첨부
        - 없으면 → 새 티켓 생성 + 스크린샷 첨부

        매개변수:
        - test_id: 테스트 ID (예: "FR-008")
        - test_name: 테스트 이름
        - error_short: 짧은 에러 메시지
        - error_full: traceback 전체
        """
        summary = f"[FAIL] {test_id} {test_name}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. 기존 티켓 검색
        issue_key = self._search_issue(summary)

        if issue_key:
            # 2-A. 기존 티켓 있으면 댓글 추가
            comment = (
                f"재실패 발생\n"
                f"\n"
                f"시각: {timestamp}\n"
                f"에러: {error_short}\n"
                f"\n"
                f"Traceback:\n"
                f"{error_full}"
            )
            self._add_comment(issue_key, comment)
            print(f"[Jira] 기존 티켓 {issue_key} 에 댓글 추가")
        else:
            # 2-B. 없으면 새 티켓 생성
            description = self._build_description(test_id, test_name, error_short, error_full)
            issue_key = self._create_issue(summary, description)
            if issue_key:
                print(f"[Jira] 새 티켓 {issue_key} 생성")
            else:
                print(f"[Jira] 티켓 생성 실패")
                return

        # 3. 스크린샷 첨부
        screenshot_name = f"{test_id}_{timestamp.replace(':', '-').replace(' ', '_')}.png"
        if self._attach_screenshot(issue_key, screenshot_name):
            print(f"[Jira] 스크린샷 첨부 완료")
        else:
            print(f"[Jira] 스크린샷 첨부 실패")