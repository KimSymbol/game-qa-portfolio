# 역할: 2048 앱 화면을 제어하는 Page Object 클래스
# POM 패턴 - UI 요소 접근을 한 곳에 모아 테스트 코드와 분리

import time
from utils.device_utils import PACKAGE, image_diff


class GamePage:
    """
    Privacy Friendly 2048 앱 제어 클래스

    PC 게임 자동화(이미지 매칭)와 달리
    resource-id 로 UI 요소에 직접 접근하는 것이 핵심
    """

    def __init__(self, device):
        """
        매개변수:
        - device: uiautomator2 device 객체
        """
        self.d = device

    # === 내부 헬퍼 ===

    def _id(self, name):
        """
        resource-id 로 요소 선택
        예: _id("points") → org.secuso.privacyfriendly2048:id/points
        """
        return self.d(resourceId=f"{PACKAGE}:id/{name}")

    # === 앱 생명주기 ===

    def start_app(self):
        """앱 실행 후 메인 화면 대기"""
        self.d.app_start(PACKAGE, stop=True)  # stop=True: 기존 실행 중이면 종료 후 재시작
        return self.wait_main_menu()

    def stop_app(self):
        """앱 종료"""
        self.d.app_stop(PACKAGE)

    # === 화면 상태 확인 ===

    def wait_main_menu(self, timeout=10):
        """
        메인 화면 표시될 때까지 대기
        새 게임 버튼 존재 여부로 판단
        """
        return self._id("button_newGame").wait(timeout=timeout)

    def wait_game_screen(self, timeout=10):
        """
        게임 화면 표시될 때까지 대기
        스와이프 영역 존재 여부로 판단
        """
        return self._id("touch_field").wait(timeout=timeout)

    def is_main_menu(self):
        """메인 화면인지 확인"""
        return self._id("button_newGame").exists

    def is_game_screen(self):
        """게임 화면인지 확인"""
        return self._id("touch_field").exists and self._id("points").exists

    # === 동작 ===

    def start_new_game(self):
        """
        메인 화면에서 새 게임 시작
        게임 화면 진입까지 대기
        """
        self._id("button_newGame").click()
        return self.wait_game_screen()

    def continue_game(self):
        """
        메인 화면에서 이전 게임 이어하기
        게임 화면 진입까지 대기
        """
        self._id("button_continueGame").click()
        return self.wait_game_screen()

    def swipe(self, direction, wait=0.8):
        """
        게임 보드에서 스와이프

        왜 touch_field 안에서 하나?
        화면 전체 스와이프는 Android 시스템 제스처(뒤로가기)와
        충돌할 수 있어 전용 영역 안에서 수행

        매개변수:
        - direction: "left" | "right" | "up" | "down"
        - wait: 스와이프 후 애니메이션 대기 시간
        """
        self._id("touch_field").swipe(direction)
        time.sleep(wait)

    def restart(self):
        """게임 재시작 버튼 클릭"""
        self._id("restartButton").click()
        time.sleep(1)

    def press_back(self):
        """
        뒤로가기 (하드웨어 키)
        게임 화면 → 메인 화면 이동에 사용
        """
        self.d.press("back")
        time.sleep(1)

    # === 상태 조회 ===

    def get_points(self):
        """
        현재 점수 반환
        UI 속성으로 직접 읽으므로 이미지 분석보다 정확
        """
        return int(self._id("points").get_text())

    def get_record(self):
        """최고 기록 반환"""
        return int(self._id("record").get_text())

    def get_board_image(self):
        """
        보드 영역만 잘라서 반환

        왜 전체 화면이 아닌가?
        상단 상태바의 시계가 매초 변하므로
        전체 화면 비교 시 항상 '변화 있음'으로 판정되어 무의미
        """
        screen = self.d.screenshot()
        bounds = self._id("number_field").info["bounds"]
        return screen.crop((
            bounds["left"], bounds["top"],
            bounds["right"], bounds["bottom"]
        ))

    def board_changed(self, before_img, threshold=1.0):
        """
        보드가 변했는지 확인

        매개변수:
        - before_img: 비교 기준 이미지
        - threshold: 변화 판정 임계값
          측정 결과 무변화=0.000, 실제이동=6.129 이므로 1.0 으로 설정

        반환값:
        - (변화 여부, 차이값)
        """
        after_img = self.get_board_image()
        diff = image_diff(before_img, after_img)
        return diff > threshold, diff