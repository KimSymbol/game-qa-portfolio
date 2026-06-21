# 역할: 테스트 종료 후 Slack Block Kit 형식으로 결과 요약 전송

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class SlackNotifier:
    """
    Slack Incoming Webhook 으로 테스트 결과 요약 전송
    Block Kit 형식으로 보기 좋게 포맷
    """

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    def send_summary(self, total, passed, failed, duration, failures=None, jira_keys=None):
        """
        테스트 결과 요약 Slack 전송

        매개변수:
        - total: 전체 테스트 수
        - passed: 성공 수
        - failed: 실패 수
        - duration: 실행 시간 (초)
        - failures: 실패 목록 [{"test_id": "FR-008", "test_name": "몬스터 공격"}, ...]
        - jira_keys: Jira 키 딕셔너리 {"FR-008": "KAN-3", ...}
        """
        if not self.webhook_url:
            print("[Slack] Webhook URL 미설정")
            return

        # 결과 이모지
        status_emoji = "✅" if failed == 0 else "🔴"

        # 실행 시간 포맷 (초 → 분:초)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        time_str = f"{minutes}분 {seconds}초"

        # Block Kit 구성
        blocks = [
            # 헤더
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} Flare RPG QA 자동화 결과",
                    "emoji": True
                }
            },
            {"type": "divider"},
            # 결과 요약
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*📊 전체:* {total}개"},
                    {"type": "mrkdwn", "text": f"*⏱️ 실행 시간:* {time_str}"},
                    {"type": "mrkdwn", "text": f"*✅ 성공:* {passed}개"},
                    {"type": "mrkdwn", "text": f"*❌ 실패:* {failed}개"},
                ]
            },
        ]

        # 실패한 테스트 목록 (있으면)
        if failures:
            failure_lines = []
            for f in failures:
                line = f"• {f['test_id']}: {f['test_name']}"
                # Jira 키가 있으면 링크 추가
                if jira_keys and f['test_id'] in jira_keys:
                    jira_key = jira_keys[f['test_id']]
                    jira_url = os.getenv("JIRA_URL")
                    line += f" → <{jira_url}/browse/{jira_key}|{jira_key}>"
                failure_lines.append(line)

            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔴 실패한 테스트*\n" + "\n".join(failure_lines)
                }
            })

        # 전송
        payload = {"blocks": blocks}
        response = requests.post(
            self.webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            print("[Slack] 결과 요약 전송 완료")
        else:
            print(f"[Slack] 전송 실패: {response.status_code} {response.text}")