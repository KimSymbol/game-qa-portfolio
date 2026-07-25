import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"화면 크기: {screen.shape}")

# 미니맵 추정 영역 (우측 상단)
minimap = screen[40:230, 1100:1280]
_, buf = cv2.imencode(".png", minimap)
buf.tofile("debug/minimap.png")
print("minimap.png 저장 완료!")