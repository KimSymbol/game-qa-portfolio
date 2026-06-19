# 역할: 테스트 데이터 생성 실행 파일
# generator.py 의 함수들을 호출
#
# 실행 방법:
#   python main.py              → 전체 데이터 기본 건수로 생성
#   python main.py 50           → 전체 데이터 50건으로 생성
#   python main.py bugs 30      → 특정 데이터만 생성
#
# 데이터 종류:
#   - QA 관련: bugs, logs, users, testcases, characters, server
#   - 기획 관련: items, skills, monsters

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from common.logger import 로거_생성
log = 로거_생성("test-data-gen")

import generator

# 데이터 종류 → 함수 매핑
생성함수맵 = {
    "bugs"      : generator.버그리포트_생성,
    "logs"      : generator.게임로그_생성,
    "users"     : generator.유저계정_생성,
    "testcases" : generator.테스트케이스_생성,
    "characters": generator.캐릭터스탯_생성,
    "server"    : generator.서버응답_생성,
    "items"     : generator.아이템_생성,
    "skills"    : generator.스킬_생성,
    "monsters"  : generator.몬스터_생성,
}

기본건수맵 = {
    "bugs"      : 20,
    "logs"      : 50,
    "users"     : 30,
    "testcases" : 20,
    "characters": 30,
    "server"    : 100,
    "items"     : 50,
    "skills"    : 30,
    "monsters"  : 30,
}

print("🎲 테스트 데이터 생성 시작...")
print("━" * 30)

log.info(f"실행 시작 - 인자: {sys.argv[1:]}")

try:
    if len(sys.argv) == 1:
        print("📋 전체 데이터 생성 (기본 건수)")
        print("━" * 30)
        log.info("전체 데이터 기본 건수로 생성")
        for 종류, 함수 in 생성함수맵.items():
            함수(기본건수맵[종류])
            log.info(f"{종류} 생성 완료")

    elif len(sys.argv) == 2 and sys.argv[1].isdigit():
        건수 = int(sys.argv[1])
        print(f"📋 전체 데이터 {건수}건 생성")
        print("━" * 30)
        log.info(f"전체 데이터 {건수}건 생성")
        for 종류, 함수 in 생성함수맵.items():
            함수(건수)
            log.info(f"{종류} 생성 완료 ({건수}건)")

    elif len(sys.argv) >= 2:
        종류 = sys.argv[1].lower()

        if 종류 not in 생성함수맵:
            print(f"❌ 알 수 없는 종류: {종류}")
            print(f"   사용 가능: {', '.join(생성함수맵.keys())}")
            log.error(f"알 수 없는 종류: {종류}")
        else:
            건수 = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() \
                   else 기본건수맵[종류]
            log.info(f"{종류} {건수}건 생성 시작")
            생성함수맵[종류](건수)
            log.info(f"{종류} 생성 완료 ({건수}건)")

    print("━" * 30)
    print("✅ 생성 완료! 결과/ 폴더를 확인해봐요.")
    log.info("전체 생성 완료")

except Exception as e:
    log.error(f"생성 실패: {type(e).__name__}: {e}")
    print(f"❌ 생성 중 에러: {e}")