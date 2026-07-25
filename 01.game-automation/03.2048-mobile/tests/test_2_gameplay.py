# 역할: 게임플레이 동작 테스트 (TW-003 ~ TW-005)

import allure
import sys
sys.path.insert(0, ".")
from utils.device_utils import attach_screenshot


@allure.epic("2048 Mobile QA")
@allure.feature("게임플레이")
class TestGameplay:

    @allure.story("TW-003 스와이프로 타일 이동")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TW003_타일_이동(self, game_started):
        """
        TW-003: 스와이프 시 타일이 이동하는지 확인

        전제조건: 게임 화면
        테스트 단계: 왼쪽으로 스와이프
        기대 결과: 보드 이미지에 변화 발생

        왜 이미지 비교인가?
        타일은 커스텀 뷰로 그려져 UI 속성으로 값을 읽을 수 없음
        점수는 병합 시에만 오르므로 단순 이동 검증에는 부적합
        """
        before = game_started.get_board_image()
        attach_screenshot(game_started.d, "스와이프_전")

        game_started.swipe("left")

        changed, diff = game_started.board_changed(before)
        attach_screenshot(game_started.d, "스와이프_후")
        print(f"보드 차이값: {diff:.4f}")

        assert changed, f"스와이프 후 보드에 변화가 없습니다 (차이값: {diff:.4f})"

    @allure.story("TW-004 타일 병합 시 점수 증가")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TW004_병합_점수증가(self, game_started):
        """
        TW-004: 같은 숫자 타일 병합 시 점수가 증가하는지 확인

        전제조건: 게임 화면
        테스트 단계: 병합이 발생할 때까지 4방향 반복 스와이프
        기대 결과: 점수가 0보다 커짐

        왜 반복 스와이프인가?
        타일 생성 위치가 랜덤이라 단일 스와이프로 병합을 보장할 수 없음
        4방향 순환 스와이프를 반복하면 병합은 통계적으로 반드시 발생
        """
        before_points = game_started.get_points()
        print(f"시작 점수: {before_points}")

        directions = ["left", "up", "right", "down"]
        merged = False

        # 최대 20회 스와이프하며 점수 증가 감지
        for i in range(20):
            game_started.swipe(directions[i % 4], wait=0.5)
            current = game_started.get_points()
            if current > before_points:
                print(f"{i+1}번째 스와이프에서 병합 발생: {before_points} → {current}")
                merged = True
                break

        attach_screenshot(game_started.d, "병합_후")
        assert merged, "20회 스와이프 동안 병합이 발생하지 않았습니다"

    @allure.story("TW-005 재시작 시 점수 초기화")
    @allure.severity(allure.severity_level.NORMAL)
    def test_TW005_재시작_초기화(self, game_started):
        """
        TW-005: 재시작 버튼 클릭 시 점수가 초기화되는지 확인

        전제조건: 점수가 0보다 큰 게임 진행 상태
        테스트 단계: 재시작 버튼 클릭
        기대 결과: 점수가 0으로 초기화

        TW-004 에서 이미 점수를 쌓았으므로 그 상태에서 이어서 검증
        """
        before_points = game_started.get_points()
        print(f"재시작 전 점수: {before_points}")
        attach_screenshot(game_started.d, "재시작_전")

        game_started.restart()

        after_points = game_started.get_points()
        print(f"재시작 후 점수: {after_points}")
        attach_screenshot(game_started.d, "재시작_후")

        assert after_points == 0, f"재시작 후 점수가 0이 아닙니다 (현재: {after_points})"