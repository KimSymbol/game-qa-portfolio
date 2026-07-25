# debug/extract_arrow.py
import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"화면 크기: {screen.shape}")

# 대화창 우측 화살표 버튼
templates = {
    "dialog_arrow": (935, 358, 65, 40),  # 화살표 버튼
}

for name, (x, y, w, h) in templates.items():
    cropped = screen[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"assets/templates/{name}.png")
    print(f"{name}.png 저장 완료!")