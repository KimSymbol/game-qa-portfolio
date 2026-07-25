# debug/test_jira_connection.py
# 역할: Jira API 연결 테스트
# 토큰과 인증 정보가 올바른지 확인

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수 가져오기
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

print(f"JIRA_URL: {JIRA_URL}")
print(f"JIRA_EMAIL: {JIRA_EMAIL}")
print(f"JIRA_PROJECT_KEY: {JIRA_PROJECT_KEY}")
print(f"JIRA_API_TOKEN: {'설정됨' if JIRA_API_TOKEN else '미설정'}")

# 인증 설정
auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}

# 프로젝트 정보 조회로 연결 테스트
url = f"{JIRA_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}"
response = requests.get(url, headers=headers, auth=auth)

print(f"\n응답 코드: {response.status_code}")
if response.status_code == 200:
    project = response.json()
    print(f"프로젝트명: {project['name']}")
    print(f"프로젝트 키: {project['key']}")
    print("✅ 연결 성공!")
else:
    print(f"❌ 연결 실패: {response.text}")