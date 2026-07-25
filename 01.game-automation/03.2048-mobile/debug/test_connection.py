# debug/test_connection.py
import uiautomator2 as u2

# 에뮬레이터 연결
d = u2.connect()  # 기본 연결 (연결된 기기 하나면 자동)

# 기기 정보 출력
print("=== 기기 정보 ===")
info = d.info
print(f"화면 크기: {info['displayWidth']} x {info['displayHeight']}")
print(f"Android 버전: {d.device_info['version']}")
print(f"모델: {d.device_info['model']}")

# 현재 실행 중인 앱
print(f"\n현재 앱: {d.app_current()}")