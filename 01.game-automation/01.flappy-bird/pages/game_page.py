# pages/game_page.py
# 역할: Flappy Bird 게임 화면을 제어하는 Page Object 클래스
# POM 패턴 - 화면 제어 로직을 한 곳에 모아서
# 테스트 코드가 직접 pyautogui/win32 를 쓰지 않도록 분리

import pydirectinput   # pygame에 키 입력 전달 시 pyautogui보다 안정적
import win32gui        # 창 핸들 제어
import win32con        # Windows 상수 (VK_MENU 등)
import win32api        # keybd_event (Alt 키 트릭)
import ctypes          # Windows API 직접 호출
import time
from utils.screen_utils import (
    capture_game,
    find_template,
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
    Flappy Bird 게임 화면 제어 클래스
    게임의 각 화면 상태 확인과 동작을 메서드로 제공
    """

    def _get_hwnd(self):
        """
        게임 창 핸들(hwnd) 반환
        hwnd = Windows OS가 각 창에 부여하는 고유 ID
        win32gui 함수들은 창 이름 대신 hwnd로 창을 식별
        """
        return win32gui.FindWindow(None, "Flappy Bird")

    def _focus_game(self):
        """
        게임 창을 최상위로 올리고 포커스 이동
        
        왜 이렇게 복잡하나?
        - pytest 실행 중 터미널이 포커스를 붙잡고 있어서
          SetForegroundWindow 단독으로는 Windows 보안 정책에 막힘
        - Alt 키 트릭으로 Windows를 속여서 포커스 이동 허용
        - SetWindowPos로 강제 최상위 설정 후 해제
        """
        hwnd = self._get_hwnd()
        if not hwnd:
            raise Exception("Flappy Bird 창을 찾을 수 없음")

        # 강제 최상위 설정 (다른 창에 가려지지 않도록)
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
        )

        # Alt 키 트릭: Windows가 포커스 전환을 허용하도록 속임
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)                        # Alt 누름
        ctypes.windll.user32.SetForegroundWindow(hwnd)                          # 포커스 이동
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0) # Alt 뗌

        # 실제 포커스 완료될 때까지 대기 (최대 2초, 0.05초 간격으로 재확인)
        start = time.time()
        while time.time() - start < 2:
            if win32gui.GetForegroundWindow() == hwnd:  # 포커스 완료 확인
                break
            time.sleep(0.05)

        # 최상위 해제 (항상 위 상태 유지하지 않음)
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
        )

    def is_start_screen(self):
        """
        현재 화면이 시작 대기 화면인지 확인
        세 가지 템플릿이 모두 보여야 True 반환
        """
        screen = capture_game()
        return (
            find_template(screen, "title.png") and      # 타이틀 확인
            find_template(screen, "get_ready.png") and  # Get Ready! 확인
            find_template(screen, "tap.png")            # TAP 버튼 확인
        )

    def is_gameover_screen(self):
        """
        현재 화면이 게임오버 화면인지 확인
        gameover.png 템플릿이 보이면 True 반환
        """
        screen = capture_game()
        return find_template(screen, "gameover.png")

    def tap(self):
        """
        게임 창 포커스 후 스페이스바 TAP
        pydirectinput 사용 이유: pyautogui는 pygame 이벤트 루프에
        키 입력이 전달되지 않는 문제가 있어서 교체
        """
        self._focus_game()              # 최상위 + 포커스 이동
        pydirectinput.press("space")    # 스페이스바 입력

    def start_game(self):
        """
        시작 화면에서 게임 시작

        반환값:
        - True: 게임 시작 성공
        - False: 시작 화면 아님 or 전환 실패
        """
        if not self.is_start_screen():  # 시작 화면 아니면 즉시 False
            return False

        self.tap()  # 포커스 이동 후 TAP

        # TAP 후 get_ready가 사라질 때까지 최대 3초 대기
        # get_ready 사라지면 게임 시작된 것으로 판단
        return wait_for_template_to_disappear("get_ready.png", timeout=3)

    def restart_game(self):
        """
        게임오버 화면에서 재시작
        TAP 후 시작 화면(get_ready)으로 돌아오는지 확인

        반환값:
        - True: 재시작 성공 (시작 화면 복귀)
        - False: 게임오버 화면 아님 or 재시작 실패
        """
        if not self.is_gameover_screen():  # 게임오버 화면 아니면 즉시 False
            return False

        self.tap()  # 포커스 이동 후 TAP

        # _focus_game() 이 포커스 이동 후 최상위 해제하는 동안
        # 캡처가 불안정할 수 있어서 잠깐 대기
        time.sleep(0.5)

        # TAP 후 get_ready가 나타날 때까지 최대 3초 대기
        return wait_for_template("get_ready.png", timeout=3)


    def wait_for_gameover(self, timeout=5):
        """
        게임오버 화면이 나타날 때까지 대기
        게임 시작 후 TAP 없이 기다리면 새가 떨어져서 자동 게임오버
        
        반환값:
        - True: timeout 안에 게임오버 화면 감지
        - False: timeout 초과
        """
        # gameover.png 가 나타날 때까지 대기
        return wait_for_template("gameover.png", timeout=timeout)