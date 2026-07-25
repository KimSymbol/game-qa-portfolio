import cv2
import numpy as np

arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"화면 크기: height={screen.shape[0]}, width={screen.shape[1]}")

# 로고 주변 구역별로 저장해서 확인
regions = {
    "logo_try3": (130, 380, 500, 200),  # 더 넓게
    "logo_try4": (130, 380, 550, 200),  # 더더 넓게
}

for name, (x, y, w, h) in regions.items():
    cropped = screen[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"debug/{name}.png")
    print(f"{name}.png 저장 완료!")