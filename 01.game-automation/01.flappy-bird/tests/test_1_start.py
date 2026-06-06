# tests/test_1_start.py
# 역할: 게임 시작 화면 관련 테스트 케이스

import allure          # Allure 리포트 데코레이터
import sys
sys.path.insert(0, ".")
from utils.screen_utils import attach_screenshot


# @allure.epic: 최상위 분류 (프로젝트명)
# @allure.feature: 기능 분류
# @allure.story: 세부 기능
@allure.epic("Flappy Bird QA")
@allure.feature("게임 시작")
class TestStart:

    @allure.story("FB-001 시작화면 표시")
    @allure.severity(allure.severity_level.CRITICAL)  # 중요도: CRITICAL
    def test_FB001_시작화면_표시(self, game_ready):
        """
        FB-001: 게임 실행 시 시작화면이 정상적으로 표시되는지 확인

        전제조건: 게임이 실행된 상태
        테스트 단계: 현재 화면에서 시작 화면 요소 확인
        기대 결과: title, get_ready, tap 템플릿이 모두 발견됨
        """
        attach_screenshot("시작화면")  # 현재 화면 스크린샷 첨부
        assert game_ready.is_start_screen(), "시작 화면이 표시되지 않았습니다"

    @allure.story("FB-002 게임 시작")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FB002_게임시작(self, game_started):
        """
        FB-002: TAP 입력 시 게임이 정상적으로 시작되는지 확인

        전제조건: 시작 대기 화면 상태
        테스트 단계: TAP 입력 (스페이스바)
        기대 결과: 게임이 시작됨 (get_ready 사라짐)
        """
        attach_screenshot("게임시작")  # 현재 화면 스크린샷 첨부
        assert not game_started.is_start_screen(), "게임이 시작되지 않았습니다"