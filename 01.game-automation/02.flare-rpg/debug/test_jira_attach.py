# debug/test_jira_attach.py
# 역할: 스크린샷 첨부 테스트

import os
import requests
import cv2
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import sys
sys.path.insert(0, ".")
from utils.screen_utils import capture_game

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)


def attach_screenshot_to_issue(issue_key, image_bytes, filename="screenshot.png"):
    """이슈에 스크린샷 첨부"""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/attachments"
    # 파일 업로드는 multipart/form-data 형식
    # X-Atlassian-Token: no-check → CSRF 보호 우회 (Jira 필수 헤더)
    headers = {"X-Atlassian-Token": "no-check"}
    files = {"file": (filename, image_bytes, "image/png")}
    response = requests.post(url, headers=headers, auth=auth, files=files)
    return response.status_code == 200


# 현재 게임 화면 캡처
print("게임 화면 캡처 중...")
screen = capture_game()
_, buf = cv2.imencode(".png", screen)
image_bytes = buf.tobytes()
print(f"캡처 크기: {len(image_bytes)} bytes")

# KAN-1 에 첨부
print("\nKAN-1 에 스크린샷 첨부...")
success = attach_screenshot_to_issue("KAN-1", image_bytes, "test_screenshot.png")
print(f"결과: {'✅ 성공' if success else '❌ 실패'}")