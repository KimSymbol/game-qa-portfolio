# debug/extract_templates2.py
import cv2
import numpy as np

# 인벤토리 화면에서 추출
arr = np.fromfile("debug/capture_inventory.png", dtype=np.uint8)
screen = cv2.imdecode(arr, cv2.IMREAD_COLOR)
print(f"인벤토리 화면 크기: {screen.shape}")

templates_inventory = {
    "inventory": (895, 20, 200, 35),  # Inventory 텍스트
}

for name, (x, y, w, h) in templates_inventory.items():
    cropped = screen[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"assets/templates/{name}.png")
    print(f"{name}.png 저장 완료!")

# 사망 화면에서 추출
arr2 = np.fromfile("debug/capture_gameover.png", dtype=np.uint8)
screen2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)
print(f"사망 화면 크기: {screen2.shape}")

templates_gameover = {
    "gameover":  (555, 95, 175, 35),  # Game Over 텍스트
    "continue":  (490, 190, 295, 45), # Continue 버튼
}

for name, (x, y, w, h) in templates_gameover.items():
    cropped = screen2[y:y+h, x:x+w]
    _, buf = cv2.imencode(".png", cropped)
    buf.tofile(f"assets/templates/{name}.png")
    print(f"{name}.png 저장 완료!")