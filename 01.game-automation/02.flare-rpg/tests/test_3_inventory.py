# 역할: 인벤토리 관련 테스트 케이스 (FR-005 ~ FR-007)

import allure
import sys
sys.path.insert(0, ".")
from utils.screen_utils import attach_screenshot


@allure.epic("Flare RPG QA")
@allure.feature("인벤토리")
class TestInventory:

    @allure.story("FR-005 인벤토리 열기")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FR005_인벤토리_열기(self, game_playing):
        """
        FR-005: I 키 입력 시 인벤토리가 정상적으로 열리는지 확인

        전제조건: 플레이 가능 상태
        테스트 단계: I 키 입력
        기대 결과: 인벤토리 창 표시 (inventory.png 발견)
        """
        result = game_playing.open_inventory()
        attach_screenshot("인벤토리_열린_상태")
        assert result, "인벤토리가 열리지 않았습니다"

    @allure.story("FR-006 아이템 장착/해제")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FR006_아이템_장착_해제(self, game_playing):
        """
        FR-006: 아이템을 해제하고 다시 장착할 수 있는지 확인

        전제조건: 인벤토리 열린 상태, 옷이 장착되어 있음
        테스트 단계: 드래그로 해제 → 우클릭으로 재장착
        기대 결과: 해제 시 빈 슬롯, 장착 시 슬롯에 아이템 표시
        """
        # 초기 장착 상태 확인
        assert game_playing.is_slot_equipped(), "전제조건: 옷이 장착되어 있어야 함"

        # 해제 테스트
        game_playing.unequip_armor()
        attach_screenshot("해제_후_화면")
        assert game_playing.is_slot_empty(), "아이템이 해제되지 않았습니다"

        # 재장착 테스트
        game_playing.equip_armor()
        attach_screenshot("재장착_후_화면")
        assert game_playing.is_slot_equipped(), "아이템이 다시 장착되지 않았습니다"

    @allure.story("FR-007 인벤토리 닫기")
    @allure.severity(allure.severity_level.NORMAL)
    def test_FR007_인벤토리_닫기(self, game_playing):
        """
        FR-007: I 키 입력 시 인벤토리가 정상적으로 닫히는지 확인

        전제조건: 인벤토리 열린 상태
        테스트 단계: I 키 입력
        기대 결과: 인벤토리 창 사라짐
        """
        result = game_playing.close_inventory()
        attach_screenshot("인벤토리_닫힌_상태")
        assert result, "인벤토리가 닫히지 않았습니다"