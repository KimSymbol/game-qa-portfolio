import cv2
import numpy as np

# 캡처 이미지 읽기
arr = np.fromfile("debug/capture_test.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"화면 크기: {screen.shape}")

# 각 요소 좌표 (x, y, width, height)
# 아직 정확한 좌표 모름 → 일단 대략적으로 잡고 확인
templates = {
    "choose_portrait": (220, 120, 250, 40),   # Choose a Portrait 텍스트
    "create_button":   (185, 665, 310, 50),   # Create 버튼
}

for name, (x, y, w, h) in templates.items():
    cropped = screen[y:y+h, x:x+w]
    path = f"assets/templates/{name}.png"
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(path)
    print(f"{name}.png 저장 완료! 크기: {cropped.shape}")