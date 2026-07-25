# debug/test_focus.py
import sys
sys.path.insert(0, ".")
import win32gui
import time
from pages.game_page import GamePage

page = GamePage()

# 포커스 이동
page._focus_game()
time.sleep(0.5)

# 현재 포커스된 창 확인
hwnd_game = win32gui.FindWindow(None, "Flare")
hwnd_current = win32gui.GetForegroundWindow()
print(f"게임 창 hwnd: {hwnd_game}")
print(f"현재 포커스 hwnd: {hwnd_current}")
print(f"게임 창 포커스 여부: {hwnd_current == hwnd_game}")

# 클릭 시도
print("클릭 시도...")
page._click(700, 410)