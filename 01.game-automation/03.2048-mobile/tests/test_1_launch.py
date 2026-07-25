# 역할: 앱 실행 및 게임 진입 테스트 (TW-001 ~ TW-002)

import allure
import sys
sys.path.insert(0, ".")
from utils.device_utils import attach_screenshot


@allure.epic("2048 Mobile QA")
@allure.feature("앱 실행")
class TestLaunch:

    @allure.story("TW-001 앱 실행 후 메인 화면 표시")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_TW001_메인화면_표시(self, app_launched):
        """
        TW-001: 앱 실행 시 메인 화면이 정상 표시되는지 확인

        전제조건: 앱 설치된 상태
        테스트 단계: 앱 실행
        기대 결과: 새 게임 버튼이 표시됨
        """
        attach_screenshot(app_launched.d, "메인화면")
        assert app_launched.is_main_menu(), "메인 화면이 표시되지 않았습니다"

    @allure.story("TW-002 새 게임 시작")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_TW002_새게임_시작(self, game_started):
        """
        TW-002: 새 게임 버튼 클릭 시 게임 화면으로 진입하는지 확인

        전제조건: 메인 화면
        테스트 단계: START NEW GAME 클릭
        기대 결과: 게임 보드와 점수 표시, 점수는 0
        """
        attach_screenshot(game_started.d, "게임화면")
        assert game_started.is_game_screen(), "게임 화면이 표시되지 않았습니다"
        assert game_started.get_points() == 0, "새 게임 시작 시 점수가 0이 아닙니다"