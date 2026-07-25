import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"화면 크기: {screen.shape}")

templates = {
    "delete_confirm": (500, 245, 300, 35),  # Delete this save? 텍스트
    "yes_button":     (490, 375, 300, 40),  # Yes 버튼
}

for name, (x, y, w, h) in templates.items():
    cropped = screen[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"assets/templates/{name}.png")
    print(f"{name}.png 저장 완료!")