# debug/test_combat_state.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
from utils.screen_utils import capture_game
import cv2
import numpy as np
import time

page = GamePage()

# 좀비 위치까지 이동
print("이동 중...")
page.move_to_monster()
print("이동 완료")

# 이동 완료 직후 화면 캡처
screen = capture_game()
cv2.circle(screen, (700, 410), 15, (0, 0, 255), 3)
_, buf = cv2.imencode(".png", screen)
buf.tofile("debug/before_attack.png")
print("before_attack.png 저장 완료")

# 게임오버 여부 확인
print(f"게임오버 상태: {page.is_gameover()}")