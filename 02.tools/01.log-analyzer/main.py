# 역할: 로그 파일 분석 실행 파일
# qa_tools.py 의 함수들을 호출해서 분석 → 출력 → 엑셀 저장까지 진행
#
# 실행 방법:
#   python main.py                    → bug_log.txt 기본 분석
#   python main.py today.txt          → 파일 지정
#   python main.py a.txt b.txt        → 여러 파일
#   python main.py logs/              → 폴더 안 txt 전부 분석

import sys
from pathlib import Path

# qa_tools.py 가 있는 폴더를 Python 경로에 추가
# → main.py 와 같은 폴더에 있는 qa_tools.py 를 import 할 수 있게 됨
sys.path.append(str(Path(__file__).parent))

import qa_tools


def 분석_실행(파일명):
    """
    로그 파일 하나를 분석해서 결과 출력 + 엑셀 저장

    매개변수:
    - 파일명: 분석할 로그 파일 이름 또는 경로

    동작 순서:
    1. 로그 파일 읽기
    2. ERROR 로그만 필터링
    3. 버그 ID / 시간 추출
    4. 중복 버그 감지
    5. 이전 결과와 비교 (신규/해결 버그 추적)
    6. 터미널에 통계 출력
    7. 엑셀 리포트 저장
    """
    print(f"\n🔍 [{파일명}] 분석 시작...")
    print("━" * 30)

    # 1. 로그 파일 읽기 → 줄 목록 반환
    전체로그 = qa_tools.로그_읽기(str(파일명))
    if not 전체로그:
        return  # 파일이 없거나 비어있으면 중단

    # 2. ERROR 포함 줄만 필터링
    에러로그 = qa_tools.에러_필터링(전체로그)

    # 3. 각 에러 로그에서 버그 ID / 시간 추출
    #    컴프리헨션으로 딕셔너리 리스트 생성
    버그목록 = [qa_tools.버그정보_추출(로그) for 로그 in 에러로그]

    # 4. 같은 버그 ID가 2회 이상 발생한 항목 탐지
    중복결과 = qa_tools.중복_감지(버그목록)

    # 5. bug_history.json 과 비교해서 신규/해결 버그 추적
    비교결과 = qa_tools.히스토리_비교(버그목록)

    # 6. 유형별 건수 계산
    error수   = sum(1 for 로그 in 전체로그 if "ERROR"   in 로그)
    warning수 = sum(1 for 로그 in 전체로그 if "WARNING" in 로그)
    info수    = sum(1 for 로그 in 전체로그 if "INFO"    in 로그)
    버그ID목록 = [버그["버그ID"] for 버그 in 버그목록]

    # 통계 출력
    print(f"총 로그 수    : {len(전체로그)}건")
    print(f"ERROR         : {error수}건 🔴")
    print(f"WARNING       : {warning수}건 🟡")
    print(f"INFO          : {info수}건 🟢")
    print(f"버그 ID 목록  : {버그ID목록}")
    print("━" * 30)

    # 중복 버그 출력
    if 중복결과:
        print("⚠️  중복 발생 버그:")
        for id, 횟수 in 중복결과.items():
            print(f"   {id} → {횟수}회 발생")
    else:
        print("✅ 중복 버그 없음")

    print("━" * 30)

    # 변경 사항 출력
    if 비교결과["신규"]:
        print(f"🆕 신규 버그  : {비교결과['신규']}")
    if 비교결과["해결"]:
        print(f"✅ 해결 버그  : {비교결과['해결']}")
    if not 비교결과["신규"] and not 비교결과["해결"]:
        print("변경 사항 없음")

    print("━" * 30)

    # 7. 분석 결과를 5시트 엑셀 파일로 저장
    저장경로 = qa_tools.엑셀_저장(버그목록, 전체로그, 비교결과, 중복결과)
    print(f"✅ 저장 완료: {저장경로}")


# ── 커맨드라인 인자에 따라 실행 방식 결정 ──
if len(sys.argv) == 1:
    # 인자 없음 → 기본 파일 분석
    분석_실행("bug_log.txt")

else:
    인자 = Path(sys.argv[1])

    if 인자.is_dir():
        # 폴더 지정 → 폴더 안 모든 .txt 파일 분석
        파일목록 = list(인자.glob("*.txt"))
        if not 파일목록:
            print("❌ 폴더 안에 txt 파일이 없어요:", 인자)
        else:
            print(f"📂 폴더 분석 시작: {인자} ({len(파일목록)}개 파일)")
            for 파일 in 파일목록:
                분석_실행(파일)
    else:
        # 파일 하나 또는 여러 개 지정
        for 파일명 in sys.argv[1:]:
            분석_실행(파일명)