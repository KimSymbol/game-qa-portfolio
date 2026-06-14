# 역할: 게임오버 후 재시작 테스트 케이스 (FR-010)

import allure
import pytest
import sys
sys.path.insert(0, ".")
from utils.screen_utils import attach_screenshot


@allure.epic("Flare RPG QA")
@allure.feature("재시작")
@pytest.mark.slow  # FR-008, FR-009 후 진행되므로 slow 마커
class TestGameOver:

    @allure.story("FR-010 게임오버 후 재시작")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FR010_재시작(self, game_gameover):
        """
        FR-010: 게임오버 화면에서 Continue 버튼 클릭 시 재시작 되는지 확인

        전제조건: 게임오버 화면 상태
        테스트 단계: Continue 버튼 클릭
        기대 결과: 게임오버 화면 사라지고 플레이 화면 복귀
        """
        # 게임오버 화면인지 확인
        assert game_gameover.is_gameover(), "전제조건: 게임오버 화면이어야 함"
        attach_screenshot("게임오버_화면")

        # Continue 클릭으로 재시작
        result = game_gameover.click_continue()
        attach_screenshot("재시작_후_화면")

        assert result, "재시작에 실패했습니다"