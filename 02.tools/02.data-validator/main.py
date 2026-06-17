# 역할: CSV 파일의 데이터 무결성을 자동으로 검증하는 실행 파일
# validator.py 의 함수들을 호출해서 검사 → 출력 → 엑셀 저장까지 진행
#
# 실행 방법:
#   python main.py bugs.csv                    → 파일 지정
#   python main.py a.csv b.csv                 → 여러 파일
#   python main.py data/                       → 폴더 안 csv 전부 검사

import sys
from pathlib import Path

# validator.py 가 있는 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

import validator


def 검증_시작(파일명):
    """
    파일 하나를 검증해서 결과 출력 + 엑셀 저장

    매개변수:
    - 파일명: 검사할 CSV 파일 이름 또는 경로
    """
    print(f"\n📋 [{파일명}] 데이터 검증 시작...")
    print("━" * 30)

    결과 = validator.검증_실행(파일명)
    if 결과 is None:
        return

    print("━" * 30)

    오류수 = len(결과["오류목록"])
    if 오류수 == 0:
        print("🎉 문제 없음! 데이터가 깨끗해요!")
    else:
        print(f"⚠️  총 {오류수}건의 문제 발견")

    print(f"✅ 검증 리포트 저장: {결과['리포트']}")


# ── 커맨드라인 인자에 따라 실행 방식 결정 ──
if len(sys.argv) == 1:
    # 인자 없음 → 사용법 안내
    print("❌ 파일을 지정해주세요")
    print("")
    print("사용법:")
    print("  python main.py bugs.csv")
    print("  python main.py 03.test-data-gen/결과/bugs_2026-06-17.csv")
    print("  python main.py a.csv b.csv")
    print("  python main.py data/")

else:
    인자 = Path(sys.argv[1])

    if 인자.is_dir():
        # 폴더 지정 → 폴더 안 모든 .csv 파일 검사
        파일목록 = list(인자.glob("*.csv"))
        if not 파일목록:
            print("❌ 폴더 안에 csv 파일이 없어요:", 인자)
        else:
            print(f"📂 폴더 검증 시작: {인자} ({len(파일목록)}개 파일)")
            for 파일 in 파일목록:
                검증_시작(str(파일))
    else:
        # 파일 하나 또는 여러 개 지정
        for 파일명 in sys.argv[1:]:
            검증_시작(파일명)