# debug/test_inventory.py
import sys
sys.path.insert(0, ".")
from pages.game_page import GamePage
import time

page = GamePage()

# 인벤토리 이미 열린 상태에서
print(f"인벤토리 열림: {page.is_inventory_open()}")
print(f"장착 상태: {page.is_slot_equipped()}")

print("\n아이템 해제 중...")
page.unequip_armor()
time.sleep(1)
print(f"해제 후 빈 슬롯: {page.is_slot_empty()}")

print("\n아이템 장착 중...")
page.equip_armor()
time.sleep(1)
print(f"장착 후 슬롯: {page.is_slot_equipped()}")