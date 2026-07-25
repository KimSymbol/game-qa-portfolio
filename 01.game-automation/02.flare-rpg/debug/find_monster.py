# debug/find_monster.py
import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)

# 몬스터 추정 위치 표시 (빨간 점 그리기)
test_points = [(700, 280), (680, 290), (720, 270)]

for x, y in test_points:
    cv2.circle(screen, (x, y), 10, (0, 0, 255), 2)

_, buf = cv2.imencode(".png", screen)
buf.tofile("debug/monster_points.png")
print("저장 완료!")