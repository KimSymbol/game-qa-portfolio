# tests/test_2_gameover.py
# 역할: 게임오버 화면 관련 테스트 케이스

import allure          # Allure 리포트 데코레이터
import sys
sys.path.insert(0, ".")
from utils.screen_utils import attach_screenshot


@allure.epic("Flappy Bird QA")
@allure.feature("게임오버")
class TestGameOver:

    @allure.story("FB-003 게임오버 화면 표시")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FB003_게임오버_화면_표시(self, game_over):
        """
        FB-003: 새가 추락/충돌 시 게임오버 화면이 표시되는지 확인

        전제조건: game_over fixture 가 자동으로 게임오버 유발
        테스트 단계: 게임오버 템플릿 감지
        기대 결과: gameover.png 템플릿 발견
        """
        attach_screenshot("게임오버화면")  # 현재 화면 스크린샷 첨부
        assert game_over.is_gameover_screen(), "게임오버 화면이 표시되지 않았습니다"

    @allure.story("FB-004 게임오버 후 재시작")
    @allure.severity(allure.severity_level.NORMAL)
    def test_FB004_게임오버_후_재시작(self, game_over):
        """
        FB-004: 게임오버 후 TAP 시 재시작 가능한지 확인

        전제조건: game_over fixture 가 게임오버 상태 준비
        테스트 단계: TAP 입력 후 시작 화면 복귀 확인
        기대 결과: 시작 화면(get_ready)으로 돌아옴
        """
        result = game_over.restart_game()
        attach_screenshot("재시작후화면")  # 재시작 후 화면 스크린샷 첨부
        assert result, "재시작에 실패했습니다"