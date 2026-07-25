# debug/test_skip_dialog.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
from utils.screen_utils import capture_game
import cv2
import numpy as np

page = GamePage()
result = page.skip_dialog()
print(f"대화 스킵 결과: {result}")

# 결과 화면 캡처
screen = capture_game()
_, buf = cv2.imencode(".png", screen)
buf.tofile("debug/after_dialog.png")
print("after_dialog.png 저장 완료!")