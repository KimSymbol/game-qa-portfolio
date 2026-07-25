# debug/test_move_to_monster.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
from utils.screen_utils import capture_game
import cv2
import numpy as np

page = GamePage()
print("몬스터 위치까지 이동 중...")
page.move_to_monster()
print("이동 완료")

# 이동 후 화면 캡처
screen = capture_game()
_, buf = cv2.imencode(".png", screen)
buf.tofile("debug/after_move.png")
print("after_move.png 저장 완료!")