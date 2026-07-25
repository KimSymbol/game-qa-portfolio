# debug/test_app_launch.py
import uiautomator2 as u2
import time

d = u2.connect()

# 앱 패키지명
PACKAGE = "org.secuso.privacyfriendly2048"

# 앱 실행
print("앱 실행 중...")
d.app_start(PACKAGE)
time.sleep(3)

# 현재 앱 확인
current = d.app_current()
print(f"현재 앱: {current}")

# 스크린샷 저장
d.screenshot("debug/app_launch.png")
print("스크린샷 저장 완료: debug/app_launch.png")