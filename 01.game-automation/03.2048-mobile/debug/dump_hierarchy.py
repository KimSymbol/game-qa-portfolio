# debug/dump_hierarchy.py
import uiautomator2 as u2

d = u2.connect()

# 현재 화면의 UI 계층 구조를 XML 로 덤프
xml = d.dump_hierarchy()

# 파일로 저장
with open("debug/hierarchy.xml", "w", encoding="utf-8") as f:
    f.write(xml)

print("hierarchy.xml 저장 완료")

# 클릭 가능한 요소만 간추려서 출력
print("\n=== 클릭 가능한 요소 ===")
for elem in d.xpath('//*[@clickable="true"]').all():
    info = elem.info
    print(f"text: {info.get('text')!r} | id: {info.get('resourceName')} | class: {info.get('className')}")

# 텍스트가 있는 요소 출력
print("\n=== 텍스트 있는 요소 ===")
for elem in d.xpath('//*[string-length(@text) > 0]').all():
    info = elem.info
    print(f"text: {info.get('text')!r} | id: {info.get('resourceName')}")