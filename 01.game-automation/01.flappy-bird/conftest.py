# conftest.py
import pytest
import time
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage


def pytest_runtest_teardown(item, nextitem):
    """
    pytest hook: 각 테스트 종료 후 자동 실행
    다음 테스트가 있을 경우 1초 대기

    왜 필요한가?
    테스트가 너무 빠르게 넘어가면
    - 사람이 육안으로 화면 확인 불가
    - 시연 영상 녹화 시 각 단계 구분 어려움
    """
    if nextitem is not None:  # 다음 테스트가 있을 경우에만 대기
        time.sleep(1)         # 1초 대기


@pytest.fixture(scope="session")
def game():
    """
    GamePage 인스턴스 반환
    scope="session" → 전체 pytest 실행에서 하나의 인스턴스 공유
    test_1_start.py, test_2_gameover.py 모두 같은 인스턴스 사용
    """
    return GamePage()


@pytest.fixture(scope="session")
def game_ready(game):
    """
    시작 화면 상태 확인
    scope="session" → 전체 테스트에서 한 번만 실행
    FB-001 이 시작 화면을 확인하고 그 상태를 이후 테스트에 전달
    """
    assert game.is_start_screen(), "전제조건: 시작 화면이어야 합니다"
    return game


@pytest.fixture(scope="session")
def game_started(game_ready):
    """
    게임 시작까지 진행
    scope="session" → FB-002 실행 후 플레이 중 상태를 이후 테스트에 전달
    FB-003 이 이 상태를 이어받아 게임오버 대기
    """
    # 게임 시작 (TAP 입력)
    game_ready.start_game()
    return game_ready


@pytest.fixture(scope="session")
def game_over(game_started):
    """
    플레이 중 상태에서 게임오버될 때까지 대기
    scope="session" → FB-003, FB-004 가 같은 게임오버 상태 공유
    TAP 없이 방치하면 새가 떨어져서 자동 게임오버
    """
    # TAP 없이 기다리면 새가 떨어져서 자동 게임오버
    assert game_started.wait_for_gameover(timeout=5), "게임오버 상태 만들기 실패"
    return game_started