# debug/test_slack.py
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv("SLACK_WEBHOOK_URL")
print(f"Webhook URL 설정됨: {bool(webhook_url)}")

# 간단한 메시지 전송
payload = {"text": "🎮 Flare RPG QA Bot 연결 테스트!"}
response = requests.post(webhook_url, data=json.dumps(payload))

print(f"응답 코드: {response.status_code}")
print(f"응답 내용: {response.text}")