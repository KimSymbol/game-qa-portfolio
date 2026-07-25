# debug/extract_hp.py
import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"화면 크기: {screen.shape}")

# 캐릭터 체력바 (좌측 상단 빨간색)
player_hp = screen[5:25, 25:250]
_, buf = cv2.imencode(".png", player_hp)
buf.tofile("debug/player_hp.png")

# 몬스터 체력바 (상단 중앙 보라색)
monster_hp = screen[30:55, 540:760]
_, buf = cv2.imencode(".png", monster_hp)
buf.tofile("debug/monster_hp.png")

print("저장 완료!")