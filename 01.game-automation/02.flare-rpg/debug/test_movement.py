# debug/test_movement.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage

page = GamePage()
print("우측 이동 테스트...")
result = page.move_character("right", duration=1.0)
print(f"이동 성공: {result}")