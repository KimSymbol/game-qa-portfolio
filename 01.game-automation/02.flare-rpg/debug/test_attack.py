# debug/test_attack.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
import time

page = GamePage()

print("좀비 공격 시도...")
page._click(700, 410)
time.sleep(2)
print("완료")