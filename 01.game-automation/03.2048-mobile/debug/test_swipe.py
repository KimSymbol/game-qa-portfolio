# debug/test_swipe.py
import uiautomator2 as u2
import time

d = u2.connect()
PACKAGE = "org.secuso.privacyfriendly2048"


def get_board_image():
    """보드 영역만 잘라서 반환"""
    # 전체 화면 캡처 (PIL Image 객체)
    screen = d.screenshot()
    # 보드 영역 좌표
    board = d(resourceId=f"{PACKAGE}:id/number_field").info["bounds"]
    # crop(left, top, right, bottom)
    return screen.crop((board["left"], board["top"], board["right"], board["bottom"]))


def get_points():
    """현재 점수 반환"""
    return int(d(resourceId=f"{PACKAGE}:id/points").get_text())


# 스와이프 전 상태
before_img = get_board_image()
before_points = get_points()
print(f"스와이프 전 점수: {before_points}")
before_img.save("debug/board_before.png")

# touch_field 안에서 왼쪽 스와이프
d(resourceId=f"{PACKAGE}:id/touch_field").swipe("left")
time.sleep(1)  # 애니메이션 대기

# 스와이프 후 상태
after_img = get_board_image()
after_points = get_points()
print(f"스와이프 후 점수: {after_points}")
after_img.save("debug/board_after.png")

# 이미지 차이 계산
import numpy as np
diff = np.array(before_img.convert("RGB"), dtype=int) - np.array(after_img.convert("RGB"), dtype=int)
mean_diff = np.abs(diff).mean()
print(f"보드 이미지 차이값: {mean_diff:.3f}")