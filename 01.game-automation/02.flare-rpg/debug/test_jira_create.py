# debug/test_jira_create.py
# 역할: Jira 티켓 생성 테스트

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
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# 티켓 생성 데이터
payload = json.dumps({
    "fields": {
        "project": {"key": JIRA_PROJECT_KEY},
        "summary": "[TEST] Jira API 연동 테스트",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "이것은 API 연동 테스트 티켓입니다."}
                    ]
                }
            ]
        },
        "issuetype": {"name": "버그"}
    }
})

url = f"{JIRA_URL}/rest/api/3/issue"
response = requests.post(url, data=payload, headers=headers, auth=auth)

print(f"응답 코드: {response.status_code}")
if response.status_code == 201:
    issue = response.json()
    print(f"✅ 티켓 생성 성공!")
    print(f"이슈 키: {issue['key']}")
    print(f"이슈 URL: {JIRA_URL}/browse/{issue['key']}")
else:
    print(f"❌ 티켓 생성 실패: {response.text}")