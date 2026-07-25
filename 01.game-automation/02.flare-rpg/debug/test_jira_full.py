# debug/test_jira_full.py
# 역할: 검색, 댓글 추가, 스크린샷 첨부 통합 테스트

import os
import requests
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json", "Content-Type": "application/json"}


def search_issue_by_summary(summary):
    """제목으로 이슈 검색"""
    # JQL: Jira Query Language
    # summary ~ "..." → 제목 포함 검색
    jql = f'project = {JIRA_PROJECT_KEY} AND summary ~ "\\"{summary}\\""'
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    payload = json.dumps({"jql": jql, "fields": ["summary"]})
    response = requests.post(url, data=payload, headers=headers, auth=auth)

    if response.status_code == 200:
        issues = response.json().get("issues", [])
        return issues[0]["key"] if issues else None
    return None


def add_comment(issue_key, comment):
    """이슈에 댓글 추가"""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    payload = json.dumps({
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": comment}]
            }]
        }
    })
    response = requests.post(url, data=payload, headers=headers, auth=auth)
    return response.status_code == 201


# 테스트 시나리오
test_summary = "[TEST] Jira API 연동 테스트"

# 1. 검색
print("1. 제목으로 이슈 검색...")
key = search_issue_by_summary(test_summary)
print(f"   결과: {key}")

# 2. 댓글 추가
if key:
    print(f"\n2. {key} 에 댓글 추가...")
    success = add_comment(key, "재실패 - 댓글 자동 추가 테스트")
    print(f"   결과: {'✅ 성공' if success else '❌ 실패'}")