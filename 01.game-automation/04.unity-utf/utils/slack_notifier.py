# 역할: 테스트 종료 후 Slack Block Kit 형식으로 결과 요약 전송

import json
import os

import requests
from dotenv import load_dotenv


# ── 1. 변수 선언부 ──────────────────────────────────

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
JIRA_URL = os.getenv("JIRA_URL")
UNITY_VERSION = os.getenv("UNITY_VERSION", "6000.3.8f1")

HEADER_TITLE = "Unity QA 자동화 결과"

TEST_ENVIRONMENT = "Unity Test Framework (PlayMode / batchmode)"


# ── 2. 함수 선언부 ──────────────────────────────────

def _format_duration(seconds):
    """초 단위 시간을 '1분 20초' 형식으로 변환."""
    return f"{int(seconds // 60)}분 {int(seconds % 60)}초"


def _failure_line(failure, jira_keys):
    """실패 항목 한 줄 생성. Jira 키가 있으면 링크로 연결."""
    line = f"• {failure.test_id}: {failure.test_name}"

    jira_key = jira_keys.get(failure.test_id)
    if jira_key:
        line += f" → <{JIRA_URL}/browse/{jira_key}|{jira_key}>"

    return line


class SlackNotifier:
    """Slack Incoming Webhook 으로 테스트 결과 요약 전송."""

    def _build_blocks(self, result, jira_keys):
        """Block Kit 메시지 구조 조립."""
        status_emoji = "✅" if result.failed == 0 else "🔴"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} {HEADER_TITLE}",
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*📊 전체:* {result.total}개"},
                    {"type": "mrkdwn", "text": f"*⏱️ 실행 시간:* {_format_duration(result.duration)}"},
                    {"type": "mrkdwn", "text": f"*✅ 성공:* {result.passed}개"},
                    {"type": "mrkdwn", "text": f"*❌ 실패:* {result.failed}개"},
                    {"type": "mrkdwn", "text": f"*🎮 Unity:* {UNITY_VERSION}"},
                    {"type": "mrkdwn", "text": f"*🧪 환경:* {TEST_ENVIRONMENT}"},
                ],
            },
        ]

        if result.failures:
            lines = [_failure_line(failure, jira_keys) for failure in result.failures]
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*🔴 실패한 테스트*\n" + "\n".join(lines)},
            })

        return blocks

    def send_summary(self, result, jira_keys=None):
        """테스트 결과 요약을 Slack 으로 전송."""
        if not SLACK_WEBHOOK_URL:
            print("[Slack] Webhook URL 미설정")
            return

        blocks = self._build_blocks(result, jira_keys or {})

        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps({"blocks": blocks}),
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            print("[Slack] 결과 요약 전송 완료")
        else:
            print(f"[Slack] 전송 실패: {response.status_code}")