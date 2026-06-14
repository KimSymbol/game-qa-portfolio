# 역할: 게임 시작 흐름 관련 테스트 케이스 (FR-001 ~ FR-003)

import allure          # Allure 리포트 데코레이터
import sys
sys.path.insert(0, ".")  # 프로젝트 루트를 모듈 탐색 경로에 추가
from utils.screen_utils import attach_screenshot


# @allure.epic: 최상위 분류 (프로젝트명)
# @allure.feature: 기능 분류
# @allure.story: 세부 기능
@allure.epic("Flare RPG QA")
@allure.feature("게임 시작")
class TestStart:

    @allure.story("FR-001 메인메뉴 화면 표시")
    @allure.severity(allure.severity_level.CRITICAL)  # 중요도: CRITICAL
    def test_FR001_메인메뉴_표시(self, game_main_menu):
        """
        FR-001: 게임 실행 시 메인메뉴 화면이 정상적으로 표시되는지 확인

        전제조건: 게임이 실행된 상태
        테스트 단계: 현재 화면에서 메인메뉴 요소 확인
        기대 결과: logo, play_game 템플릿이 모두 발견됨
        """
        attach_screenshot("메인메뉴_화면")  # 현재 화면 스크린샷 첨부
        assert game_main_menu.is_main_menu(), "메인메뉴 화면이 표시되지 않았습니다"

    @allure.story("FR-002 Play Game 클릭 시 다음 화면 이동")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FR002_play_game_클릭(self, game_save_select):
        """
        FR-002: Play Game 클릭 시 다음 화면으로 정상 이동하는지 확인

        전제조건: 메인메뉴 화면
        테스트 단계: Play Game 버튼 클릭
        기대 결과: 세이브 선택 화면 or 캐릭터 생성 화면 표시
                (세이브 유무에 따라 다름)
        """
        attach_screenshot("Play_Game_클릭_후")
        # 세이브 선택 화면 or 캐릭터 생성 화면 둘 다 정상
        is_save_select = game_save_select.is_save_select_screen()
        is_character_create = game_save_select.is_character_create_screen()
        assert is_save_select or is_character_create, \
            "Play Game 클릭 후 다음 화면으로 이동하지 못했습니다"

    @allure.story("FR-003 캐릭터 생성 화면 이동")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FR003_캐릭터_생성_화면(self, game_character_create):
        """
        FR-003: 세이브 삭제 후 New Game 클릭 시 캐릭터 생성 화면으로 이동하는지 확인

        전제조건: 세이브 선택 화면
        테스트 단계: Delete Save → Yes → New Game 클릭
        기대 결과: 캐릭터 생성 화면 표시 (choose_portrait 템플릿 발견)
        """
        attach_screenshot("캐릭터_생성_화면")
        assert game_character_create.is_character_create_screen(), "캐릭터 생성 화면이 표시되지 않았습니다"