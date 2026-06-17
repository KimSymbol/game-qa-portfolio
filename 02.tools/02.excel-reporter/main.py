# 역할: CSV 버그 데이터를 읽어 엑셀 리포트를 생성하는 실행 파일
# reporter.py 의 함수들을 호출해서 분석 → 출력 → 엑셀 저장까지 진행
#
# 실행 방법:
#   python main.py bugs.csv                    → 파일 지정
#   python main.py a.csv b.csv                 → 여러 파일
#   python main.py data/                       → 폴더 안 csv 전부 분석

import sys
from pathlib import Path

# reporter.py 가 있는 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

import reporter


def 리포트_실행(파일명):
    """
    CSV 파일 하나를 읽어서 통계 출력 + 엑셀 리포트 저장

    매개변수:
    - 파일명: 분석할 CSV 파일 이름 또는 경로

    동작 순서:
    1. CSV 파일 읽기 → DataFrame 생성
    2. 터미널에 통계 출력 (총 건수, 해결률 등)
    3. 4시트 엑셀 리포트 생성 및 저장
    """
    print(f"\n📊 [{파일명}] 리포트 생성 시작...")
    print("━" * 30)

    # 1. CSV 읽기 → DataFrame 반환
    df = reporter.데이터_읽기(파일명)
    if df is None:
        return

    # 2. 핵심 지표 계산 및 출력
    총버그 = len(df)
    해결   = len(df[df["상태"] == "해결"])
    진행중 = len(df[df["상태"] == "진행중"])
    미해결 = len(df[df["상태"] == "미해결"])
    해결률 = round(해결 / 총버그 * 100, 1) if 총버그 > 0 else 0

    print(f"총 버그 수  : {총버그}건")
    print(f"해결        : {해결}건 ✅")
    print(f"진행중      : {진행중}건 🟡")
    print(f"미해결      : {미해결}건 🔴")
    print(f"해결률      : {해결률}%")
    print("━" * 30)

    # 3. 5시트 엑셀 리포트 생성 및 저장
    저장경로 = reporter.리포트_생성(df)
    print(f"✅ 저장 완료: {저장경로}")


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
        # 폴더 지정 → 폴더 안 모든 .csv 파일 분석
        파일목록 = list(인자.glob("*.csv"))
        if not 파일목록:
            print("❌ 폴더 안에 csv 파일이 없어요:", 인자)
        else:
            print(f"📂 폴더 분석 시작: {인자} ({len(파일목록)}개 파일)")
            for 파일 in 파일목록:
                리포트_실행(str(파일))
    else:
        # 파일 하나 또는 여러 개 지정
        for 파일명 in sys.argv[1:]:
            리포트_실행(파일명)