# debug/test_utils.py
import sys
sys.path.insert(0, ".")
from utils.screen_utils import capture_game, find_template

screen = capture_game()
print(f"캡처 크기: {screen.shape}")
print(f"logo: {find_template(screen, 'logo.png')}")
print(f"play_game: {find_template(screen, 'play_game.png')}")