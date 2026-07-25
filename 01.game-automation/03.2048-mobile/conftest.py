# 역할: pytest fixture 및 실패 리포팅 hook 정의

import re
import sys
import time

import pytest

sys.path.insert(0, ".")

from pages.game_page import GamePage
from utils.bug_reporter import BugReporter
from utils.device_utils import connect_device
from utils.jira_reporter import JiraReporter
from utils.slack_notifier import SlackNotifier


# ── 1. 변수 선언부 ──────────────────────────────────

# 테스트 함수명에서 ID 와 이름을 추출하는 패턴
# 예: test_TW003_타일_이동 → ("003", "타일_이동")
TEST_NAME_PATTERN = re.compile(r"test_TW(\d+)_(.+)")

DEFAULT_SEVERITY = "critical"

# 세션 전체 결과 집계
_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "failures": [],
    "jira_keys": {},
    "start_time": 0,
}

_shared = {"device": None, "bug_reporter": None}


# ── 2. 함수 선언부 ──────────────────────────────────

def _parse_test_name(func_name):
    """테스트 함수명에서 (테스트 ID, 테스트명) 추출."""
    match = TEST_NAME_PATTERN.match(func_name)
    if match is None:
        return "UNKNOWN", func_name
    return f"TW-{match.group(1)}", match.group(2).replace("_", " ")


def _get_severity(item):
    """테스트에 지정된 Allure severity 반환. 없으면 기본값."""
    for marker in item.iter_markers("allure_label"):
        if marker.kwargs.get("label_type") == "severity" and marker.args:
            return marker.args[0]
    return DEFAULT_SEVERITY


def _report_to_jira(test_id, test_name, error_short, error_full):
    """Jira 티켓 생성 또는 댓글 추가. 실패해도 테스트 진행에 영향 없음."""
    try:
        reporter = JiraReporter(_shared["device"])
        issue_key = reporter.report_failure(test_id, test_name, error_short, error_full)
        if issue_key:
            _results["jira_keys"][test_id] = issue_key
    except Exception as error:
        print(f"[Jira] 전송 중 오류: {error}")


def _report_to_file(test_id, test_name, severity):
    """CSV/XLSX 버그 리포트 기록."""
    try:
        if _shared["bug_reporter"] is None:
            _shared["bug_reporter"] = BugReporter(_shared["device"])
        _shared["bug_reporter"].add_bug(test_id, test_name, severity)
    except Exception as error:
        print(f"[BugReport] 기록 중 오류: {error}")


def _notify_slack():
    """세션 종료 후 Slack 요약 전송."""
    try:
        notifier = SlackNotifier(_shared["device"])
        notifier.send_summary(
            total=_results["total"],
            passed=_results["passed"],
            failed=_results["failed"],
            duration=time.time() - _results["start_time"],
            failures=_results["failures"],
            jira_keys=_results["jira_keys"],
        )
    except Exception as error:
        print(f"[Slack] 전송 중 오류: {error}")


def _print_report_paths():
    """생성된 버그 리포트 경로 출력."""
    if _shared["bug_reporter"] is None:
        return

    paths = _shared["bug_reporter"].get_paths()
    for file_type, path in paths.items():
        if path:
            print(f"[BugReport] {file_type.upper()}: {path}")


def pytest_sessionstart(session):
    """세션 시작 시각 기록."""
    _results["start_time"] = time.time()


def pytest_sessionfinish(session, exitstatus):
    """세션 종료 시 Slack 알림 및 리포트 경로 출력."""
    _notify_slack()
    _print_report_paths()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 실행 결과를 집계하고 실패 시 Jira/버그리포트로 전달."""
    outcome = yield
    report = outcome.get_result()

    # setup/teardown 은 제외하고 실제 테스트 실행 단계만 집계
    if report.when != "call":
        return

    _results["total"] += 1
    test_id, test_name = _parse_test_name(item.name)

    if report.passed:
        _results["passed"] += 1
        return

    if not report.failed:
        return

    _results["failed"] += 1
    _results["failures"].append({"test_id": test_id, "test_name": test_name})

    error_short = str(call.excinfo.value) if call.excinfo else "Unknown error"
    _report_to_jira(test_id, test_name, error_short, report.longreprtext)
    _report_to_file(test_id, test_name, _get_severity(item))


@pytest.fixture(scope="session")
def device():
    """ADB 로 연결된 기기. DEVICE_SERIAL 환경변수로 대상 지정."""
    connected = connect_device()
    _shared["device"] = connected
    return connected


@pytest.fixture(scope="session")
def game(device):
    """2048 앱 Page Object."""
    return GamePage(device)


@pytest.fixture(scope="session")
def app_launched(game):
    """앱 실행 후 메인 화면까지 진입한 상태."""
    assert game.start_app(), "앱 실행 후 메인 화면 진입 실패"
    return game


@pytest.fixture(scope="session")
def game_started(app_launched):
    """새 게임 시작 후 게임 화면까지 진입한 상태."""
    assert app_launched.start_new_game(), "새 게임 시작 실패"
    return app_launched