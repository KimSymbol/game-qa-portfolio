# utils/screen_utils.py
# 역할: 게임 화면 캡처와 템플릿 매칭 관련 유틸리티 함수 모음
# 다른 모듈(pages, tests)에서 공통으로 사용하는 핵심 기능

import win32gui        # 창 핸들 제어
import win32ui         # 창 DC(Device Context) 제어
import win32con        # Windows 상수
import pyautogui       # 화면 캡처, 키보드/마우스 제어
import cv2             # OpenCV - 이미지 처리 및 템플릿 매칭
import numpy as np     # 이미지를 배열로 다루기 위한 라이브러리
import os              # 파일 경로 처리
import time            # 시간 처리
import allure          # Allure 리포트 연동
from ctypes import windll

# 템플릿 이미지가 저장된 폴더 경로
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "templates")

# 기존 방식 (상단바/테두리 가정) 대신
# 실제 픽셀 분석으로 찾은 정확한 값 사용
CROP_TOP = 0      # 상단 자르기 없음
CROP_LEFT = 0     # 좌측 자르기 없음
CROP_RIGHT = 17   # 우측 검은 여백 17픽셀
CROP_BOTTOM = 513 # 하단 게임 화면 끝 y좌표


def capture_game():
    """
    게임 창을 직접 캡처 (창이 가려져 있어도 동작)
    pyautogui 방식과 달리 창 핸들로 직접 픽셀을 읽어옴
    """
    hwnd = win32gui.FindWindow(None, "Flappy Bird")

    # 창 크기 가져오기
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # 창 DC(Device Context) 가져오기
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # 비트맵 생성
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    # 창 내용을 비트맵에 복사
    windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

    # numpy 배열로 변환
    bmp_info = bitmap.GetInfo()
    bmp_arr = bitmap.GetBitmapBits(True)
    img = np.frombuffer(bmp_arr, dtype=np.uint8)
    img = img.reshape(bmp_info["bmHeight"], bmp_info["bmWidth"], 4)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # 메모리 해제
    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    # 상단바 + 테두리 제거 후 반환
    return img[CROP_TOP:CROP_BOTTOM, CROP_LEFT:width-CROP_RIGHT]


def find_template(screen, template_name, threshold=0.8):
    """
    게임 화면(screen)에서 템플릿 이미지를 찾아 True/False 반환
    
    매개변수:
    - screen: capture_game()으로 캡처한 게임 화면 이미지
    - template_name: 찾을 템플릿 파일명 (예: "title.png")
    - threshold: 유사도 기준값 (0~1, 기본값 0.8)
    
    왜 np.fromfile을 쓰나?
    cv2.imread()는 한글 경로 미지원
    np.fromfile() → cv2.imdecode() 조합으로 한글 경로 우회
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)

    # 한글 경로 우회: 바이트로 읽은 후 이미지로 디코딩
    arr = np.fromfile(template_path, dtype=np.uint8)
    template = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if template is None:
        raise Exception(f"템플릿 로드 실패: {template_path}")

    # TM_CCOEFF_NORMED: 정규화된 상관계수 방식 (0~1 사이 값 반환)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

    # 최대 유사도 값만 추출
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val >= threshold


def wait_for_template(template_name, timeout=5, interval=0.2):
    """
    특정 템플릿이 화면에 나타날 때까지 대기
    웹의 WebDriverWait과 같은 원리
    - 조건 충족 시 즉시 반환
    - timeout 초과 시 False 반환

    매개변수:
    - template_name: 기다릴 템플릿 파일명
    - timeout: 최대 대기 시간 (초, 기본값 5)
    - interval: 체크 간격 (초, 기본값 0.2)
    """
    start_time = time.time()
    while True:
        screen = capture_game()
        if find_template(screen, template_name):  # 템플릿 발견 시
            return True                           # 즉시 True 반환
        if time.time() - start_time >= timeout:   # timeout 초과 시
            return False
        time.sleep(interval)                      # interval 만큼 대기 후 재시도


def wait_for_template_to_disappear(template_name, timeout=5, interval=0.2):
    """
    특정 템플릿이 화면에서 사라질 때까지 대기

    매개변수:
    - template_name: 사라지길 기다릴 템플릿 파일명
    - timeout: 최대 대기 시간 (초, 기본값 5)
    - interval: 체크 간격 (초, 기본값 0.2)
    """
    start_time = time.time()
    while True:
        screen = capture_game()
        if not find_template(screen, template_name):  # 템플릿 없으면
            return True                               # 즉시 True 반환
        if time.time() - start_time >= timeout:       # timeout 초과 시
            return False
        time.sleep(interval)


def attach_screenshot(name="screenshot"):
    """
    현재 게임 화면을 캡처해서 Allure 리포트에 첨부
    
    매개변수:
    - name: Allure 리포트에 표시될 스크린샷 이름
    
    왜 필요한가?
    테스트 결과를 시각적으로 확인할 수 있어서
    포트폴리오 임팩트가 높아짐
    """
    screen = capture_game()

    # OpenCV 이미지 → PNG 바이트로 변환
    _, buf = cv2.imencode(".png", screen)

    # Allure 리포트에 PNG 형식으로 첨부
    allure.attach(
        buf.tobytes(),
        name=name,
        attachment_type=allure.attachment_type.PNG
    )