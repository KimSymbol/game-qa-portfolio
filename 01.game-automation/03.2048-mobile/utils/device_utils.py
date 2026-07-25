# 역할: 기기 연결, 이미지 비교, Allure 첨부 등 공통 유틸리티

import io
import os

import allure
import numpy as np
import uiautomator2 as u2
from dotenv import load_dotenv


# ── 1. 변수 선언부 ──────────────────────────────────

load_dotenv()

# 테스트 대상 앱 패키지명
PACKAGE = "org.secuso.privacyfriendly2048"

# 대상 기기 시리얼 (미설정 시 자동 선택)
# emulator-5554 → 에뮬레이터 / R5CRB30GHGW → 갤럭시 Z 플립3
DEVICE_SERIAL = os.getenv("DEVICE_SERIAL")


# ── 2. 함수 선언부 ──────────────────────────────────

def connect_device():
    """환경변수로 지정한 기기에 연결. 미지정 시 자동 선택."""
    device = u2.connect(DEVICE_SERIAL) if DEVICE_SERIAL else u2.connect()
    print(f"[Device] {device.device_info['model']} / Android {device.device_info['version']}")
    return device


def image_diff(img1, img2):
    """두 PIL 이미지의 픽셀 차이 평균 반환. 0 에 가까울수록 동일."""
    # int 로 변환해야 뺄셈 시 음수 표현 가능 (uint8 은 언더플로우 발생)
    arr1 = np.array(img1.convert("RGB"), dtype=int)
    arr2 = np.array(img2.convert("RGB"), dtype=int)
    return np.abs(arr1 - arr2).mean()


def attach_screenshot(device, name="screenshot"):
    """현재 화면을 캡처해 Allure 리포트에 첨부."""
    buffer = io.BytesIO()
    device.screenshot().save(buffer, format="PNG")
    allure.attach(
        buffer.getvalue(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )