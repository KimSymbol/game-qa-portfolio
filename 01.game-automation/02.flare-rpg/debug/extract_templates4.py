# debug/extract_templates4.py
import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"화면 크기: {screen.shape}")

templates = {
    "load_game":   (810, 360, 270, 50),  # Load Game 버튼
    "delete_save": (810, 408, 270, 50),  # Delete Save 버튼
    "new_game":    (185, 670, 300, 50),  # New Game 버튼
}

for name, (x, y, w, h) in templates.items():
    cropped = screen[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"assets/templates/{name}.png")
    print(f"{name}.png 저장 완료!")