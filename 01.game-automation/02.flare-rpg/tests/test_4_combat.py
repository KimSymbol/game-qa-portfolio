# 역할: 전투 관련 테스트 케이스 (FR-008 ~ FR-009)

import allure
import pytest
import sys
import time
import cv2
import pyautogui
import win32gui
sys.path.insert(0, ".")
from utils.screen_utils import attach_screenshot
from utils.screen_utils import wait_for_pixel_change


@allure.epic("Flare RPG QA")
@allure.feature("전투")
@pytest.mark.slow  # 전투 테스트는 시간이 오래 걸려서 slow 마커 적용
class TestCombat:

    @allure.story("FR-008 몬스터 공격")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FR008_몬스터_공격(self, game_combat):
        """
        FR-008: 몬스터 공격 시 몬스터 체력이 감소하는지 확인

        전제조건: 몬스터 근처 위치 (좀비가 다가오는 중)
        테스트 단계: 좀비 위치로 마우스 호버 → 체력바 확인 → 공격 → 체력 비교
        기대 결과: 몬스터 체력바 픽셀 변화 감지

        체력바는 마우스 호버 시에만 표시되므로 호버 유지 상태로 비교
        """

        # 좀비가 다가올 때까지 충분히 대기
        time.sleep(3.0)

        # 좀비 위치로 마우스 호버 (체력바 표시 유도)
        hwnd = game_combat._get_hwnd()
        left, top, _, _ = win32gui.GetWindowRect(hwnd)
        TITLE_BAR = 31
        BORDER = 8
        abs_x = left + BORDER + 700
        abs_y = top + TITLE_BAR + 410
        pyautogui.moveTo(abs_x, abs_y)
        time.sleep(0.5)  # 체력바 표시 대기

        # 공격 전 몬스터 체력바 영역 캡처
        before = game_combat.get_monster_hp_area()
        attach_screenshot("공격_전")

        # 공격 (마우스 위치 유지하며 클릭)
        pyautogui.click(abs_x, abs_y)
        time.sleep(0.5)

        # 공격 후 체력바 캡처 (마우스 위치 그대로)
        after = game_combat.get_monster_hp_area()
        attach_screenshot("공격_후")

        # 픽셀 차이 계산
        diff = cv2.absdiff(before, after)
        mean_diff = diff.mean()
        print(f"몬스터 체력바 차이값: {mean_diff:.3f}")

        assert mean_diff > 1.0, "몬스터 체력이 감소하지 않았습니다"

    @allure.story("FR-009 피격")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_FR009_피격(self, game_combat):
        """
        FR-009: 몬스터에게 피격 시 캐릭터 체력이 감소하는지 확인

        전제조건: 몬스터 근처 위치 (전투 중)
        테스트 단계: 좀비가 공격할 때까지 대기 (최대 15초)
        기대 결과: 캐릭터 체력바 픽셀 변화 감지

        왜 wait_for_pixel_change 사용?
        좀비 공격 속도가 일정하지 않아서 고정 sleep 보다
        변화 감지될 때까지 대기하는 게 안정적
        """
        

        attach_screenshot("피격_전")
        # 캐릭터 체력바 변화 감지될 때까지 최대 15초 대기
        result = wait_for_pixel_change(
            game_combat.get_player_hp_area,
            timeout=15,
            interval=0.5,
            threshold=1.0
        )
        attach_screenshot("피격_후")
        assert result, "캐릭터 체력이 감소하지 않았습니다"