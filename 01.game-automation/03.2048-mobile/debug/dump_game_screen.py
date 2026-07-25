# debug/dump_game_screen.py
import uiautomator2 as u2
import time

d = u2.connect()
PACKAGE = "org.secuso.privacyfriendly2048"

# 새 게임 시작
d(resourceId=f"{PACKAGE}:id/button_newGame").click()
time.sleep(2)

# 게임 화면 스크린샷
d.screenshot("debug/game_screen.png")

# UI 계층 덤프
with open("debug/hierarchy_game.xml", "w", encoding="utf-8") as f:
    f.write(d.dump_hierarchy())
print("hierarchy_game.xml 저장 완료")

# resource-id 가 있는 요소 전부 출력
print("\n=== resource-id 있는 요소 ===")
for elem in d.xpath('//*[@resource-id!=""]').all():
    info = elem.info
    rid = info.get("resourceName")
    txt = info.get("text")
    print(f"id: {rid} | text: {txt!r}")