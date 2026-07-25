# debug/test_board_bounds.py
import uiautomator2 as u2

d = u2.connect()
PACKAGE = "org.secuso.privacyfriendly2048"

# 보드 컨테이너 요소의 좌표 정보
board = d(resourceId=f"{PACKAGE}:id/number_field")
print(f"보드 존재 여부: {board.exists}")

if board.exists:
    info = board.info
    bounds = info["bounds"]
    print(f"보드 영역: {bounds}")
    print(f"  좌상단: ({bounds['left']}, {bounds['top']})")
    print(f"  우하단: ({bounds['right']}, {bounds['bottom']})")
    print(f"  크기: {bounds['right'] - bounds['left']} x {bounds['bottom'] - bounds['top']}")

# 스와이프 영역도 확인
touch = d(resourceId=f"{PACKAGE}:id/touch_field")
print(f"\n스와이프 영역 존재: {touch.exists}")
if touch.exists:
    print(f"스와이프 영역: {touch.info['bounds']}")

# 점수 확인
points = d(resourceId=f"{PACKAGE}:id/points")
print(f"\n현재 점수: {points.get_text()}")