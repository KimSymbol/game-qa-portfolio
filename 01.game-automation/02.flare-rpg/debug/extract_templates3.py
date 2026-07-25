# debug/extract_templates3.py
import cv2
import numpy as np

arr2 = np.fromfile("debug/capture_unequipped.png", dtype=np.uint8)
screen2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

templates2 = {
    "slot_empty": (1148, 125, 65, 65),  # 빈 슬롯 (같은 위치)
}

for name, (x, y, w, h) in templates2.items():
    cropped = screen2[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"assets/templates/{name}.png")
    print(f"{name}.png 저장 완료!")