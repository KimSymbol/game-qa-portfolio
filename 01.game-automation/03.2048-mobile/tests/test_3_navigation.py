# tests/test_3_navigation.py
# 역할: 화면 이동 및 게임 상태 유지 테스트 (TW-006 ~ TW-007)

import allure
import sys
sys.path.insert(0, ".")
from utils.device_utils import attach_screenshot


@allure.epic("2048 Mobile QA")
@allure.feature("화면 이동")
class TestNavigation:

    @allure.story("TW-006 뒤로가기로 메인 화면 복귀")
    @allure.severity(allure.severity_level.NORMAL)
    def test_TW006_뒤로가기_메인복귀(self, game_started):
        """
        TW-006: 게임 중 뒤로가기 시 메인 화면으로 복귀하는지 확인

        전제조건: 게임 화면
        테스트 단계: Android 뒤로가기 키 입력
        기대 결과: 메인 화면 표시

        모바일 특화 테스트 - PC 게임에는 없는 하드웨어 키 동작 검증
        """
        # 이후 TW-007 에서 비교할 점수를 미리 만들어둠
        game_started.swipe("left")
        game_started.swipe("up")
        points_before_exit = game_started.get_points()
        print(f"나가기 전 점수: {points_before_exit}")

        # 다음 테스트에서 쓰도록 인스턴스에 저장
        game_started.saved_points = points_before_exit

        attach_screenshot(game_started.d, "뒤로가기_전")
        game_started.press_back()
        attach_screenshot(game_started.d, "뒤로가기_후")

        assert game_started.is_main_menu(), "뒤로가기 후 메인 화면이 표시되지 않았습니다"

    @allure.story("TW-007 이어하기로 게임 상태 복원")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TW007_이어하기_상태복원(self, game_started):
        """
        TW-007: CONTINUE GAME 클릭 시 이전 게임 상태가 복원되는지 확인

        전제조건: 게임을 진행하다 메인 화면으로 나온 상태
        테스트 단계: CONTINUE GAME 클릭
        기대 결과: 나가기 전과 동일한 점수로 복원

        데이터 영속성 검증 - 앱이 게임 상태를 올바르게 저장/복원하는지 확인
        """
        assert game_started.is_main_menu(), "전제조건: 메인 화면이어야 합니다"

        assert game_started.continue_game(), "이어하기 후 게임 화면 진입 실패"

        restored_points = game_started.get_points()
        print(f"복원된 점수: {restored_points} (저장된 점수: {game_started.saved_points})")
        attach_screenshot(game_started.d, "이어하기_후")

        assert restored_points == game_started.saved_points, (
            f"점수가 복원되지 않았습니다 "
            f"(기대: {game_started.saved_points}, 실제: {restored_points})"
        )