# 역할: 게임플레이 동작 테스트 (TW-003 ~ TW-005)

import allure
import sys

sys.path.insert(0, ".")

from utils.device_utils import attach_screenshot


# ── 1. 변수 선언부 ──────────────────────────────────

SWIPE_DIRECTIONS = ["left", "up", "right", "down"]

# 병합 발생까지 허용할 최대 스와이프 횟수
MAX_MERGE_ATTEMPTS = 20


# ── 2. 함수 선언부 ──────────────────────────────────

def _swipe_until_board_changes(game):
    """
    보드에 변화가 생길 때까지 4방향을 순회하며 스와이프한다.

    초기 타일이 이미 특정 방향 끝에 붙어 있으면 그 방향 스와이프는
    변화를 만들지 못하므로, 단일 방향 검증은 랜덤 배치에 취약하다.

    반환값: (변화 여부, 마지막 차이값, 시도한 방향)
    """
    for direction in SWIPE_DIRECTIONS:
        before = game.get_board_image()
        game.swipe(direction)
        changed, diff = game.board_changed(before)

        if changed:
            return True, diff, direction

    return False, 0.0, None


def _swipe_until_points_increase(game):
    """
    점수가 오를 때까지 4방향을 순회하며 반복 스와이프한다.

    타일 생성 위치가 랜덤이라 단일 스와이프로 병합을 보장할 수 없다.

    반환값: (병합 여부, 시작 점수, 최종 점수, 시도 횟수)
    """
    start_points = game.get_points()

    for attempt in range(MAX_MERGE_ATTEMPTS):
        game.swipe(SWIPE_DIRECTIONS[attempt % len(SWIPE_DIRECTIONS)], wait=0.5)
        current_points = game.get_points()

        if current_points > start_points:
            return True, start_points, current_points, attempt + 1

    return False, start_points, game.get_points(), MAX_MERGE_ATTEMPTS


def _assert_board_changed(game):
    """스와이프로 보드가 변했는지 검증."""
    changed, diff, direction = _swipe_until_board_changes(game)
    attach_screenshot(game.d, "스와이프_후")
    print(f"이동 방향: {direction} / 보드 차이값: {diff:.4f}")

    assert changed, "4방향 모두 스와이프했으나 보드에 변화가 없습니다"


def _assert_points_increased(game):
    """병합으로 점수가 증가했는지 검증."""
    merged, start, end, attempts = _swipe_until_points_increase(game)
    attach_screenshot(game.d, "병합_후")
    print(f"{attempts}회 스와이프 / 점수 {start} → {end}")

    assert merged, f"{MAX_MERGE_ATTEMPTS}회 스와이프 동안 병합이 발생하지 않았습니다"


def _assert_points_reset(game):
    """재시작 후 점수가 0으로 초기화됐는지 검증."""
    before_points = game.get_points()
    game.restart()
    after_points = game.get_points()

    attach_screenshot(game.d, "재시작_후")
    print(f"점수 {before_points} → {after_points}")

    assert after_points == 0, f"재시작 후 점수가 0이 아닙니다 (현재: {after_points})"


# ── 3. 메인 실행부 ──────────────────────────────────

@allure.epic("2048 Mobile QA")
@allure.feature("게임플레이")
class TestGameplay:

    @allure.story("TW-003 스와이프로 타일 이동")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TW003_타일_이동(self, game_started):
        """
        [TW-003]
        스와이프 시 타일이 이동한다

        절차:
        1. 보드에 변화가 생길 때까지 4방향 순회 스와이프

        기대:
        보드 이미지 차이값이 임계값을 초과
        """
        _assert_board_changed(game_started)

    @allure.story("TW-004 타일 병합 시 점수 증가")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TW004_병합_점수증가(self, game_started):
        """
        [TW-004]
        같은 숫자 타일이 병합되면 점수가 증가한다

        절차:
        1. 점수가 오를 때까지 4방향 순회 반복 스와이프

        기대:
        점수가 시작값보다 증가
        """
        _assert_points_increased(game_started)

    @allure.story("TW-005 재시작 시 점수 초기화")
    @allure.severity(allure.severity_level.NORMAL)
    def test_TW005_재시작_초기화(self, game_started):
        """
        [TW-005]
        재시작하면 점수가 초기화된다

        절차:
        1. 재시작 버튼 클릭

        기대:
        점수가 0으로 초기화
        """
        _assert_points_reset(game_started)