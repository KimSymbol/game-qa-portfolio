# debug/test_create.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
from utils.screen_utils import capture_game
import cv2
import numpy as np
import time

page = GamePage()

# 캐릭터 생성 화면인지 확인
print(f"캐릭터 생성 화면: {page.is_character_create_screen()}")

# Create 버튼 클릭
page._click_template("create_button.png")
time.sleep(2)

# 클릭 후 화면 캡처
screen = capture_game()
_, buf = cv2.imencode(".png", screen)
buf.tofile("debug/after_create.png")
print("after_create.png 저장 완료!")