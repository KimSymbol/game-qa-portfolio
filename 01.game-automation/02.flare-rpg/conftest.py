# 역할: pytest 전체에서 공유하는 fixture 와 hook 정의

import pytest
import re
import time
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
from utils.jira_reporter import JiraReporter
from utils.bug_reporter import BugReporter
from utils.slack_notifier import SlackNotifier


# === 전역 변수 (테스트 결과 수집용) ===
_test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "failures": [],   # 실패 목록
    "jira_keys": {},  # {test_id: jira_key}
    "start_time": 0,
}
_bug_reporter = BugReporter()


def pytest_sessionstart(session):
    """
    pytest hook: 세션 시작 시 호출
    전체 실행 시간 측정 시작
    """
    _test_results["start_time"] = time.time()


def pytest_runtest_teardown(item, nextitem):
    """
    pytest hook: 각 테스트 종료 후 자동 실행
    다음 테스트가 있을 경우 1초 대기
    """
    if nextitem is not None:
        time.sleep(1)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest hook: 각 테스트 단계 종료 후 자동 실행
    call 단계 결과만 수집 (setup/teardown 제외)

    실패 시:
    1. Jira 티켓 생성/댓글 추가
    2. CSV/XLSX 버그 리포트 기록
    3. 결과 수집 (Slack 요약용)
    """
    outcome = yield
    report = outcome.get_result()

    # call 단계만 처리
    if report.when != "call":
        return

    # 결과 카운트 증가
    _test_results["total"] += 1

    # 테스트 함수명에서 ID, 이름 추출
    func_name = item.name
    match = re.match(r"test_FR(\d+)_(.+)", func_name)
    if match:
        test_id = f"FR-{match.group(1)}"
        test_name = match.group(2).replace("_", " ")
    else:
        test_id = "UNKNOWN"
        test_name = func_name

    if report.passed:
        _test_results["passed"] += 1
    elif report.failed:
        _test_results["failed"] += 1
        _test_results["failures"].append({
            "test_id": test_id,
            "test_name": test_name,
        })

        # 에러 정보 추출
        error_short = str(call.excinfo.value) if call.excinfo else "Unknown error"
        error_full = report.longreprtext

        # Allure severity 추출
        severity = "critical"  # 기본값
        for marker in item.iter_markers("allure_label"):
            if marker.kwargs.get("label_type") == "severity":
                severity = marker.args[0] if marker.args else "critical"

        # 1. Jira 티켓 생성/댓글
        try:
            reporter = JiraReporter()
            reporter.report_failure(test_id, test_name, error_short, error_full)
        except Exception as e:
            print(f"[Jira] 전송 중 오류: {e}")

        # 2. CSV/XLSX 버그 리포트
        try:
            _bug_reporter.add_bug(test_id, test_name, severity)
        except Exception as e:
            print(f"[BugReport] 기록 중 오류: {e}")


def pytest_sessionfinish(session, exitstatus):
    """
    pytest hook: 전체 세션 종료 시 호출
    Slack 요약 알림 전송
    """
    duration = time.time() - _test_results["start_time"]

    # Slack 요약 전송
    try:
        notifier = SlackNotifier()
        notifier.send_summary(
            total=_test_results["total"],
            passed=_test_results["passed"],
            failed=_test_results["failed"],
            duration=duration,
            failures=_test_results["failures"],
            jira_keys=_test_results["jira_keys"],
        )
    except Exception as e:
        print(f"[Slack] 전송 중 오류: {e}")

    # 버그 리포트 경로 출력
    paths = _bug_reporter.get_paths()
    if paths["csv"]:
        print(f"\n[BugReport] CSV: {paths['csv']}")
    if paths["xlsx"]:
        print(f"[BugReport] XLSX: {paths['xlsx']}")


# === Fixture 정의 ===

@pytest.fixture(scope="session")
def game():
    """GamePage 인스턴스 반환"""
    return GamePage()


@pytest.fixture(scope="session")
def game_main_menu(game):
    """메인메뉴 화면 상태 확인"""
    assert game.is_main_menu(), "전제조건: 메인메뉴 화면이어야 함"
    return game


@pytest.fixture(scope="session")
def game_save_select(game_main_menu):
    """Play Game 클릭 후 다음 화면 이동"""
    result = game_main_menu.click_play_game()
    game_main_menu.play_game_result = result
    return game_main_menu


@pytest.fixture(scope="session")
def game_character_create(game_save_select):
    """캐릭터 생성 화면 진입 보장"""
    if game_save_select.play_game_result == "save_select":
        game_save_select.delete_save_and_new_game()
    return game_save_select


@pytest.fixture(scope="session")
def game_playing(game_character_create):
    """
    캐릭터 생성 → 스토리 씬 → 튜토리얼 대화 스킵
    실제 플레이 가능 상태까지 진입
    """
    game_character_create.click_create()
    for _ in range(8):
        game_character_create._click(640, 360)
        time.sleep(1)
    time.sleep(2)
    game_character_create.skip_dialog()
    return game_character_create


@pytest.fixture(scope="session")
def game_combat(game_playing):
    """몬스터 위치까지 이동"""
    game_playing.move_to_monster()
    return game_playing


@pytest.fixture(scope="session")
def game_gameover(game_combat):
    """좀비에게 피격당해 사망 → 게임오버 상태"""
    assert game_combat.wait_until_dead(timeout=60), "사망 상태 만들기 실패"
    return game_combat