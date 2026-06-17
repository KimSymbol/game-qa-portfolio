# 역할: 테스트 데이터 생성 실행 파일
# generator.py 의 함수들을 호출해서 원하는 데이터를 생성
#
# 실행 방법:
#   python main.py              → 전체 데이터 기본 건수로 생성
#   python main.py 50           → 전체 데이터 50건으로 생성
#   python main.py bugs 30      → 버그 리포트만 30건 생성
#   python main.py logs 100     → 게임 로그만 100줄 생성
#   python main.py users 20     → 유저 계정만 20건 생성
#   python main.py testcases 15 → 테스트 케이스만 15건 생성
#   python main.py characters 25→ 캐릭터 스탯만 25건 생성
#   python main.py server 200   → 서버 응답만 200건 생성

import sys
from pathlib import Path

# generator.py 가 있는 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

import generator

# ── 데이터 종류 → 함수 매핑 ──
생성함수맵 = {
    "bugs"      : generator.버그리포트_생성,
    "logs"      : generator.게임로그_생성,
    "users"     : generator.유저계정_생성,
    "testcases" : generator.테스트케이스_생성,
    "characters": generator.캐릭터스탯_생성,
    "server"    : generator.서버응답_생성,
}

# ── 기본 생성 건수 ──
기본건수맵 = {
    "bugs"      : 20,
    "logs"      : 50,
    "users"     : 30,
    "testcases" : 20,
    "characters": 30,
    "server"    : 100,
}

print("🎲 테스트 데이터 생성 시작...")
print("━" * 30)

if len(sys.argv) == 1:
    # 인자 없음 → 전체 데이터 기본 건수로 생성
    print("📋 전체 데이터 생성 (기본 건수)")
    print("━" * 30)
    for 종류, 함수 in 생성함수맵.items():
        함수(기본건수맵[종류])

elif len(sys.argv) == 2 and sys.argv[1].isdigit():
    # 숫자만 있으면 → 전체 데이터를 해당 건수로 생성
    건수 = int(sys.argv[1])
    print(f"📋 전체 데이터 {건수}건 생성")
    print("━" * 30)
    for 종류, 함수 in 생성함수맵.items():
        함수(건수)

elif len(sys.argv) >= 2:
    # 종류 지정 → 해당 데이터만 생성
    종류 = sys.argv[1].lower()

    if 종류 not in 생성함수맵:
        print(f"❌ 알 수 없는 종류: {종류}")
        print(f"   사용 가능: {', '.join(생성함수맵.keys())}")
    else:
        건수 = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() \
               else 기본건수맵[종류]
        생성함수맵[종류](건수)

print("━" * 30)
print("✅ 생성 완료! 결과/ 폴더를 확인해봐요.")