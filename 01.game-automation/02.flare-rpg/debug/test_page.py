# debug/test_page.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage

page = GamePage()
print(f"메인메뉴: {page.is_main_menu()}")
page.click_play_game()
print(f"세이브 선택 화면: {page.is_save_select_screen()}")
result = page.delete_save_and_new_game()
print(f"캐릭터 생성 화면: {result}")