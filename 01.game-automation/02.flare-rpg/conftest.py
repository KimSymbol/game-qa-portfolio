# 역할: pytest 전체에서 공유하는 fixture 정의
# session scope → 전체 pytest 실행에서 한 번만 실행
#                 테스트 간 게임 상태를 이어받아 자연스러운 플레이 사이클 재현

import pytest
import re
import time
import sys
sys.path.insert(0, ".")  # 프로젝트 루트를 모듈 탐색 경로에 추가
from pages.game_page import GamePage
from utils.jira_reporter import JiraReporter


def pytest_runtest_teardown(item, nextitem):
    """
    pytest hook: 각 테스트 종료 후 자동 실행
    다음 테스트가 있을 경우 1초 대기

    왜 필요한가?
    테스트가 너무 빠르게 넘어가면
    - 사람이 육안으로 화면 확인 불가
    - 시연 영상 녹화 시 각 단계 구분 어려움
    """
    if nextitem is not None:
        time.sleep(1)


@pytest.fixture(scope="session")
def game():
    """
    GamePage 인스턴스 반환
    scope="session" → 전체 pytest 실행에서 하나의 인스턴스 공유
    """
    return GamePage()


@pytest.fixture(scope="session")
def game_main_menu(game):
    """
    메인메뉴 화면 상태 확인
    FR-001 의 전제조건
    """
    assert game.is_main_menu(), "전제조건: 메인메뉴 화면이어야 함"
    return game


@pytest.fixture(scope="session")
def game_save_select(game_main_menu):
    """
    메인메뉴에서 Play Game 클릭
    세이브 유무와 상관없이 다음 화면으로 이동

    반환값:
    - game: GamePage 인스턴스
    - 다음 화면 상태 (세이브 선택 화면 or 캐릭터 생성 화면)
    """
    result = game_main_menu.click_play_game()
    # 결과를 game 인스턴스에 저장해서 다음 fixture 에서 확인 가능
    game_main_menu.play_game_result = result
    return game_main_menu


@pytest.fixture(scope="session")
def game_character_create(game_save_select):
    """
    캐릭터 생성 화면 진입 보장
    세이브 있으면 → Delete Save → Yes → New Game
    세이브 없으면 → 이미 캐릭터 생성 화면이므로 그대로
    """
    if game_save_select.play_game_result == "save_select":
        # 세이브 있음: 삭제 후 New Game
        game_save_select.delete_save_and_new_game()
    # 세이브 없음: 이미 캐릭터 생성 화면

    return game_save_select


@pytest.fixture(scope="session")
def game_playing(game_character_create):
    """
    캐릭터 생성 완료 후 스토리 씬 + 튜토리얼 대화 스킵
    실제 게임 플레이 가능한 상태까지 진입
    FR-004 이후 테스트의 전제조건

    흐름:
    Create 버튼 클릭 → 스토리 씬 8회 클릭 → 로딩 → 튜토리얼 대화 스킵
    """
    # Create 버튼 클릭으로 게임 시작
    game_character_create.click_create()

    # 스토리 씬 스킵 (8번 클릭)
    for _ in range(8):
        game_character_create._click(640, 360)
        time.sleep(1)

    # 로딩 + 튜토리얼 대화 스킵
    time.sleep(2)  # 로딩 대기
    game_character_create.skip_dialog()

    return game_character_create


@pytest.fixture(scope="session")
def game_combat(game_playing):
    """
    플레이 가능 상태에서 몬스터 위치까지 이동
    FR-008, FR-009 전제조건

    @pytest.mark.slow 권장 - 이동에 약 30초 소요
    """
    game_playing.move_to_monster()
    return game_playing


@pytest.fixture(scope="session")
def game_gameover(game_combat):
    """
    몬스터 만나서 사망 → 게임오버 상태 만들기
    FR-010 전제조건
    
    공격 안 하고 좀비에게 피격당해서 사망 유도
    """
    # 사망할 때까지 대기 (최대 30초)
    assert game_combat.wait_until_dead(timeout=30), "사망 상태 만들기 실패"
    return game_combat


@pytest.fixture(scope="session")
def game_gameover(game_combat):
    """
    좀비에게 피격당해 사망 → 게임오버 상태 만들기
    FR-010 전제조건

    공격 안 하고 좀비 옆에서 대기 → 자동 피격 → 사망
    """
    # 사망할 때까지 최대 60초 대기
    # FR-008, FR-009 후 이미 좀비랑 전투 중이므로 시간이 지나면 자연스럽게 사망
    assert game_combat.wait_until_dead(timeout=60), "사망 상태 만들기 실패"
    return game_combat


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest hook: 각 테스트의 각 단계(setup/call/teardown) 종료 후 자동 실행
    실패 감지 시 Jira 티켓 생성/댓글 추가

    hookwrapper=True 의미:
    pytest 가 만든 report 객체를 가로채서 우리가 추가 처리 가능

    동작:
    1. 테스트 실행 단계(call) 에서 실패 발생 시에만 처리
    2. 테스트 ID 와 이름을 함수명에서 추출
    3. JiraReporter 호출
    """
    # pytest 기본 동작 수행 후 결과 받기
    outcome = yield
    report = outcome.get_result()

    # call 단계(실제 테스트 실행) 실패만 처리
    # setup/teardown 실패는 제외 (fixture 문제는 별도 이슈)
    if report.when != "call" or not report.failed:
        return

    # 테스트 함수명에서 ID 추출
    # 예: test_FR008_몬스터_공격 → "FR-008", "몬스터 공격"
    func_name = item.name
    match = re.match(r"test_FR(\d+)_(.+)", func_name)
    if match:
        test_id = f"FR-{match.group(1)}"
        test_name = match.group(2).replace("_", " ")
    else:
        # 매칭 안 되면 함수명 그대로
        test_id = "UNKNOWN"
        test_name = func_name

    # 에러 정보 추출
    error_short = str(call.excinfo.value) if call.excinfo else "Unknown error"
    error_full = report.longreprtext  # traceback 전체

    # Jira 전송
    try:
        reporter = JiraReporter()
        reporter.report_failure(test_id, test_name, error_short, error_full)
    except Exception as e:
        # Jira 전송 실패해도 pytest 자체는 계속 진행
        print(f"[Jira] 전송 중 오류: {e}")