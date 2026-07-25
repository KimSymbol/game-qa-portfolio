# debug/test_story.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
from utils.screen_utils import capture_game
import cv2
import numpy as np
import time

page = GamePage()

# 화면 중앙 클릭으로 스토리 넘기기 시도 (8번)
for i in range(8):
    page._click(640, 360)  # 화면 중앙
    time.sleep(1)
    print(f"{i+1}번째 클릭 완료")

# 클릭 후 화면 캡처
screen = capture_game()
_, buf = cv2.imencode(".png", screen)
buf.tofile("debug/after_story.png")
print("after_story.png 저장 완료!")