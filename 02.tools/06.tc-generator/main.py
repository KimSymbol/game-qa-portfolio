# 역할: JSON 사양 파일로부터 TC를 자동 생성하는 실행 파일
#
# 실행 방법:
#   python main.py                       → specs/ 안 전체 사양 처리
#   python main.py login.json            → 특정 사양 1개
#   python main.py login.json shop.json  → 여러 사양

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from common.logger import 로거_생성
log = 로거_생성("tc-generator")

import tc_generator


def 결과_출력(결과):
    """단일 사양 처리 결과 출력"""
    if 결과 is None:
        print("[ERROR] TC 생성 실패")
        return

    print(f"\n생성 완료!")
    print(f"   CSV : {결과['csv']}")
    print(f"   XLSX: {결과['xlsx']}")           # ← 추가
    print(f"   총 {결과['건수']}건의 TC")
    print(f"   ├── 동등분할:   {결과['기법별']['동등분할']}건")
    print(f"   ├── 경계값:     {결과['기법별']['경계값']}건")
    print(f"   └── 결정테이블: {결과['기법별']['결정테이블']}건")


print("테스트 케이스 자동 생성기")
print("━" * 30)

if len(sys.argv) == 1:
    # specs/ 폴더 전체 처리
    print("specs/ 폴더 전체 사양 처리 시작")
    결과목록 = tc_generator.전체_사양_TC_생성()

    if not 결과목록:
        print("[ERROR] 처리된 사양이 없습니다")
    else:
        print(f"\n{'=' * 50}")
        print(f"📊 전체 처리 완료: {len(결과목록)}개 사양")
        print(f"{'=' * 50}")
        for 결과 in 결과목록:
            결과_출력(결과)
else:
    for 사양파일 in sys.argv[1:]:
        결과 = tc_generator.전체_TC_생성(사양파일)
        결과_출력(결과)
        print("━" * 30)

print()
print("다음 단계:")
print("   생성된 TC를 data-validator 로 검증:")
print("   python 02.data-validator/main.py 06.tc-generator/결과/testcases_login_latest.csv")