# debug/find_coords.py
import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)

# Play Game 버튼 위치 찾기
template_arr = np.fromfile("assets/templates/play_game.png", dtype=np.uint8)
template = cv2.imdecode(template_arr, cv2.IMREAD_COLOR)

result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
_, _, _, max_loc = cv2.minMaxLoc(result)
h, w = template.shape[:2]

# 버튼 중앙 좌표 계산
center_x = max_loc[0] + w // 2
center_y = max_loc[1] + h // 2
print(f"Play Game 버튼 중앙 좌표: x={center_x}, y={center_y}")