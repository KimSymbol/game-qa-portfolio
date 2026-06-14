# 역할: Flare RPG 게임 화면을 제어하는 Page Object 클래스
# POM 패턴 - 화면 제어 로직을 한 곳에 모아서
# 테스트 코드가 직접 pyautogui/win32 를 쓰지 않도록 분리

import pydirectinput   # 게임에 키 입력 전달
import pyautogui       # 마우스 클릭 제어
import win32gui        # 창 핸들 제어
import win32con        # Windows 상수 (VK_MENU 등)
import win32api        # keybd_event (Alt 키 트릭)
import ctypes          # Windows API 직접 호출
import cv2             # 미니맵 비교용
import time
from utils.screen_utils import (
    capture_game,
    find_template,
    find_template_location,
    wait_for_template,
    wait_for_template_to_disappear
)

# SetWindowPos 에 사용하는 Windows 상수
HWND_TOPMOST = -1    # 항상 최상위 설정
HWND_NOTOPMOST = -2  # 최상위 해제
SWP_NOMOVE = 0x0002  # 위치 변경 없음
SWP_NOSIZE = 0x0001  # 크기 변경 없음


class GamePage:
    """
    Flare RPG 게임 화면 제어 클래스
    게임의 각 화면 상태 확인과 동작을 메서드로 제공
    """

    def _get_hwnd(self):
        """
        게임 창 핸들(hwnd) 반환
        hwnd = Windows OS가 각 창에 부여하는 고유 ID
        """
        return win32gui.FindWindow(None, "Flare")

    def _focus_game(self):
        """
        게임 창을 최상위로 올리고 포커스 이동
        Alt 키 트릭으로 Windows 보안 정책 우회
        """
        hwnd = self._get_hwnd()
        if not hwnd:
            raise Exception("Flare 창을 찾을 수 없음")

        # 강제 최상위 설정
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
        )

        # Alt 키 트릭: Windows가 포커스 전환을 허용하도록 속임
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)                        # Alt 누름
        ctypes.windll.user32.SetForegroundWindow(hwnd)                          # 포커스 이동
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0) # Alt 뗌

        # 실제 포커스 완료될 때까지 대기 (최대 2초)
        start = time.time()
        while time.time() - start < 2:
            if win32gui.GetForegroundWindow() == hwnd:
                break
            time.sleep(0.05)

        # 최상위 해제
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
        )

    def _click(self, x, y):
        """
        게임 창 포커스 후 마우스 클릭
        게임 창 기준 상대 좌표로 클릭
        클라이언트 영역 기준으로 보정 (상단바 + 테두리 제외)
        """
        self._focus_game()

        hwnd = self._get_hwnd()
        left, top, _, _ = win32gui.GetWindowRect(hwnd)

        # 상단바(31px) + 좌측 테두리(8px) 보정
        TITLE_BAR = 31
        BORDER = 8
        abs_x = left + BORDER + x
        abs_y = top + TITLE_BAR + y

        pyautogui.click(abs_x, abs_y)
        time.sleep(0.3)

    def _click_template(self, template_name):
        """
        템플릿 위치를 자동으로 찾아서 클릭
        좌표 하드코딩 없이 템플릿 매칭으로 클릭 위치 결정
        """
        screen = capture_game()
        loc = find_template_location(screen, template_name)
        if loc is None:
            return False  # 템플릿 못 찾으면 클릭 안 함
        self._click(loc[0], loc[1])
        return True

    def _press(self, key):
        """
        게임 창 포커스 후 키 입력
        pydirectinput 사용 이유: pyautogui는 게임 이벤트 루프에
        키 입력이 전달되지 않는 문제가 있어서 교체
        """
        self._focus_game()
        pydirectinput.press(key)

    def is_main_menu(self):
        """메인메뉴 화면인지 확인"""
        screen = capture_game()
        return (
            find_template(screen, "logo.png") and
            find_template(screen, "play_game.png")
        )

    def is_character_create_screen(self):
        """캐릭터 생성 화면인지 확인"""
        screen = capture_game()
        return find_template(screen, "choose_portrait.png")

    def is_inventory_open(self):
        """인벤토리가 열려있는지 확인"""
        screen = capture_game()
        return find_template(screen, "inventory.png")

    def is_slot_equipped(self):
        """장착 슬롯에 아이템이 있는지 확인"""
        screen = capture_game()
        return find_template(screen, "slot_equipped.png")

    def is_slot_empty(self):
        """장착 슬롯이 비어있는지 확인"""
        screen = capture_game()
        return find_template(screen, "slot_empty.png")

    def is_gameover(self):
        """게임오버 화면인지 확인"""
        screen = capture_game()
        return find_template(screen, "gameover.png")

    def click_play_game(self):
        """
        메인메뉴에서 Play Game 버튼 클릭
        세이브 유무에 따라 다음 화면이 다름

        반환값:
        - "save_select": 세이브 선택 화면 진입 (세이브 있음)
        - "character_create": 캐릭터 생성 화면 진입 (세이브 없음)
        - False: 클릭 실패
        """
        if not self._click_template("play_game.png"):
            return False

        # 세이브 선택 화면 or 캐릭터 생성 화면 둘 중 하나 대기
        start = time.time()
        while time.time() - start < 5:
            screen = capture_game()
            if find_template(screen, "load_game.png"):
                return "save_select"
            if find_template(screen, "choose_portrait.png"):
                return "character_create"
            time.sleep(0.2)
        return False
        
    def click_create(self):
        """
        캐릭터 생성 화면에서 Create 버튼 클릭
        템플릿으로 버튼 위치 자동 탐지 후 클릭
        """
        if not self._click_template("create_button.png"):
            return False
        return wait_for_template_to_disappear("choose_portrait.png", timeout=10)

    def open_inventory(self):
        """I 키로 인벤토리 열기"""
        self._press("i")
        return wait_for_template("inventory.png", timeout=3)

    def close_inventory(self):
        """I 키로 인벤토리 닫기"""
        self._press("i")
        return wait_for_template_to_disappear("inventory.png", timeout=3)

    def click_continue(self):
        """
        게임오버 화면에서 Continue 버튼 클릭
        템플릿으로 버튼 위치 자동 탐지 후 클릭
        """
        if not self._click_template("continue.png"):
            return False
        return wait_for_template_to_disappear("gameover.png", timeout=5)

    def is_save_select_screen(self):
        """세이브 파일 선택 화면인지 확인"""
        screen = capture_game()
        return find_template(screen, "load_game.png")

    def delete_save_and_new_game(self):
        """
        기존 세이브 삭제 후 New Game 클릭
        테스트 시작 전 항상 동일한 상태 만들기 위해 사용
        세이브가 없으면 바로 캐릭터 생성 화면으로 이동
        """
        screen = capture_game()

        # 세이브 있으면 삭제 후 New Game
        if find_template(screen, "delete_save.png"):
            self._click_template("delete_save.png")
            time.sleep(0.5)

        # New Game 클릭
        self._click_template("new_game.png")
        return wait_for_template("choose_portrait.png", timeout=5)

    def delete_save_and_new_game(self):
        """
        기존 세이브 삭제 후 New Game 클릭
        테스트 시작 전 항상 동일한 상태 만들기 위해 사용
        세이브가 없으면 바로 캐릭터 생성 화면으로 이동

        흐름:
        세이브 선택 화면 → Delete Save 클릭 → 확인 창 Yes 클릭 → New Game 클릭 → 캐릭터 생성 화면
        """
        screen = capture_game()

        # 세이브 있으면 삭제 절차 진행
        if find_template(screen, "delete_save.png"):
            # Delete Save 클릭 → 확인 창 등장
            self._click_template("delete_save.png")

            # 확인 창 Yes 버튼 등장 대기 후 클릭
            if wait_for_template("yes_button.png", timeout=3):
                self._click_template("yes_button.png")
                time.sleep(0.5)  # 삭제 처리 대기

        # New Game 클릭 → 캐릭터 생성 화면 이동
        self._click_template("new_game.png")
        return wait_for_template("choose_portrait.png", timeout=5)

    def skip_dialog(self, max_clicks=20):
        """
        대화창의 화살표/X 버튼을 반복 클릭해서 대화 전부 넘김
        대화창이 사라지면 종료

        매개변수:
        - max_clicks: 최대 클릭 횟수 (무한 루프 방지)

        반환값:
        - True: 대화창 사라짐
        - False: max_clicks 초과

        동작:
        - 중간 대화: 화살표(▷) 클릭으로 다음 페이지로
        - 마지막 대화: X 버튼 클릭으로 대화창 닫기
        """
        for i in range(max_clicks):
            # 클릭 후 마우스가 버튼 위에 있으면 호버 상태라 매칭 실패
            # 마우스를 화면 좌측 상단으로 이동해서 호버 상태 해제
            pyautogui.moveTo(100, 100)
            time.sleep(0.2)

            screen = capture_game()

            # 화살표 있으면 클릭 (다음 대화 페이지로)
            if find_template(screen, "dialog_arrow.png"):
                self._click_template("dialog_arrow.png")
                time.sleep(0.5)
                continue

            # X 버튼 있으면 클릭 (마지막 대화 닫기)
            if find_template(screen, "dialog_close.png"):
                self._click_template("dialog_close.png")
                time.sleep(0.5)
                continue

            # 둘 다 없으면 대화 끝
            return True

        return False

    def get_minimap(self):
        """
        미니맵 영역만 잘라서 반환
        캐릭터 위치 변화 감지에 사용
        """
        screen = capture_game()
        # 미니맵 영역 (우측 상단)
        return screen[40:230, 1100:1280]


    def move_character(self, direction, duration=1.0):
        """
        캐릭터를 특정 방향으로 일정 시간 이동
        이동 전후 미니맵 비교로 이동 성공 여부 확인

        매개변수:
        - direction: 이동 방향 ("up", "down", "left", "right")
        - duration: 키 누르고 있는 시간 (초)

        반환값:
        - True: 이동 성공 (미니맵 변화 감지)
        - False: 이동 실패 (변화 없음)
        """
        # 방향키 매핑 (Flare RPG 기본 WASD)
        key_map = {
            "up": "w",
            "down": "s",
            "left": "a",
            "right": "d",
        }
        key = key_map.get(direction)
        if not key:
            return False

        # 게임 창 포커스
        self._focus_game()

        # 이동 전 미니맵 캡처
        before = self.get_minimap()

        # 방향키 일정 시간 동안 누르기
        pydirectinput.keyDown(key)
        time.sleep(duration)
        pydirectinput.keyUp(key)
        time.sleep(0.3)  # 미니맵 업데이트 대기

        # 이동 후 미니맵 캡처
        after = self.get_minimap()

        # 두 미니맵의 차이 계산
        # mean: 픽셀 차이의 평균, 클수록 변화가 큼
        diff = cv2.absdiff(before, after)
        mean_diff = diff.mean()
        print(f"미니맵 차이값: {mean_diff:.3f}")

        # 임계값 이상 차이나면 이동 성공
        return mean_diff > 1.0


    def _drag(self, from_x, from_y, to_x, to_y, duration=0.5):
        """
        드래그 앤 드롭 동작
        
        매개변수:
        - from_x, from_y: 시작 좌표 (게임 창 기준 상대 좌표)
        - to_x, to_y: 끝 좌표 (게임 창 기준 상대 좌표)
        - duration: 드래그 소요 시간 (초)
        """
        self._focus_game()

        hwnd = self._get_hwnd()
        left, top, _, _ = win32gui.GetWindowRect(hwnd)

        # 상단바(31px) + 좌측 테두리(8px) 보정
        TITLE_BAR = 31
        BORDER = 8
        abs_from_x = left + BORDER + from_x
        abs_from_y = top + TITLE_BAR + from_y
        abs_to_x = left + BORDER + to_x
        abs_to_y = top + TITLE_BAR + to_y

        # pyautogui 드래그
        pyautogui.moveTo(abs_from_x, abs_from_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(abs_to_x, abs_to_y, duration=duration)
        pyautogui.mouseUp()
        time.sleep(0.5)


    def _right_click(self, x, y):
        """
        게임 창 포커스 후 우클릭
        아이템 장착에 사용
        """
        self._focus_game()

        hwnd = self._get_hwnd()
        left, top, _, _ = win32gui.GetWindowRect(hwnd)

        TITLE_BAR = 31
        BORDER = 8
        abs_x = left + BORDER + x
        abs_y = top + TITLE_BAR + y

        pyautogui.rightClick(abs_x, abs_y)
        time.sleep(0.5)


    def unequip_armor(self):
        """
        옷(armor) 슬롯에서 아이템 해제
        장착 슬롯 → 인벤토리 빈 칸으로 드래그
        """
        # 옷 슬롯 → 인벤토리 빈 칸 (3번째)
        self._drag(1170, 150, 970, 95)


    def equip_armor(self):
        """
        인벤토리의 옷 아이템 우클릭으로 장착
        """
        self._right_click(970, 95)  # 빈 칸 위치 = 해제했던 위치

    def move_to_monster(self):
        """
        초기 위치에서 몬스터 위치까지 순차 이동
        수동 측정한 경로로 진행

        경로:
        1. 아래 5초
        2. 오른쪽 2초 (맵 전환)
        3. 아래 3초
        4. 왼쪽 2초
        5. 아래 2초
        6. 오른쪽 2초
        7. 아래 3초
        8. 오른쪽 3초
        9. 위 3초
        10. 오른쪽 2초
        """
        # (방향, 시간)
        path = [
            ("down",  5),
            ("right", 2),
            ("down",  3),
            ("left",  2),
            ("down",  2),
            ("right", 2),
            ("down",  3),
            ("right", 3),
            ("up",    3),
            ("right", 2),
        ]

        for direction, duration in path:
            self.move_character(direction, duration=duration)
            time.sleep(0.3)  # 각 이동 사이 잠깐 대기


    def get_player_hp_area(self):
        """
        캐릭터 체력바 영역만 잘라서 반환
        좌측 상단에 있는 빨간색 체력바
        """
        screen = capture_game()
        # 체력바 영역 (좌측 상단)
        return screen[15:45, 25:230]


    def get_monster_hp_area(self):
        """
        몬스터 체력바 영역만 잘라서 반환
        공격 시 화면 상단에 표시되는 몬스터 체력바
        """
        screen = capture_game()
        # 몬스터 체력바 영역 (상단 중앙)
        return screen[15:50, 500:800]


    def attack_monster(self):
        """
        가장 가까운 몬스터를 공격
        Flare RPG 는 마우스 좌클릭으로 공격
        화면 중앙 근처 클릭으로 캐릭터 주변 몬스터 공격
        """
        self._focus_game()

        hwnd = self._get_hwnd()
        left, top, _, _ = win32gui.GetWindowRect(hwnd)

        TITLE_BAR = 31
        BORDER = 8
        # 캐릭터 주변 (화면 중앙) 클릭
        abs_x = left + BORDER + 640
        abs_y = top + TITLE_BAR + 360

        pyautogui.click(abs_x, abs_y)
        time.sleep(0.5)


    def get_player_hp_area(self):
        """
        캐릭터 체력바 영역 반환
        좌측 상단 빨간 막대
        """
        screen = capture_game()
        return screen[5:25, 25:250]


    def get_monster_hp_area(self):
        """
        몬스터 체력바 영역 반환
        상단 중앙 보라색 막대 + 숫자
        """
        screen = capture_game()
        return screen[30:55, 540:760]


    def is_monster_in_combat(self):
        """
        몬스터와 전투 중인지 확인
        상단 중앙에 몬스터 체력바가 표시되는지 픽셀 분석으로 감지
        배경(잔디)과 다른 색상이 있으면 전투 중으로 판단
        """
        monster_area = self.get_monster_hp_area()
        # 표준편차로 변화 감지 (배경만 있으면 균일, 체력바 있으면 다양)
        std = monster_area.std()
        return std > 20  # 임계값


    def attack_monster(self, x=700, y=410, wait=2.0):
        """
        지정 위치 좌클릭으로 평타 공격
        좀비가 다가올 시간을 주기 위해 wait 만큼 대기 후 공격

        매개변수:
        - x, y: 공격 좌표 (기본값: 좀비가 다가오는 위치)
        - wait: 공격 전 대기 시간 (좀비 접근 시간)
        """
        time.sleep(wait)
        self._click(x, y)


    def wait_until_dead(self, timeout=30):
        """
        캐릭터가 사망할 때까지 대기
        게임오버 화면 표시될 때까지 기다림

        매개변수:
        - timeout: 최대 대기 시간 (초)

        반환값:
        - True: 사망 (게임오버 화면 표시)
        - False: timeout 초과
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.is_gameover():
                return True
            time.sleep(0.5)
        return False