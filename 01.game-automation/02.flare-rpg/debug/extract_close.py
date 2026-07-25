# debug/extract_close.py
import cv2
import numpy as np

arr = np.fromfile("debug/after_dialog.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)

# X 버튼 좌표
templates = {
    "dialog_close": (945, 355, 55, 45),  # X 버튼
}

for name, (x, y, w, h) in templates.items():
    cropped = screen[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"assets/templates/{name}.png")
    print(f"{name}.png 저장 완료!")