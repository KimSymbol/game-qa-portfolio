# 역할: 로그 파일 분석 실행 파일
# qa_tools.py 의 함수들을 호출해서 분석 → 출력 → 엑셀 저장까지 진행
#
# 실행 방법:
#   python main.py                    → bug_log.txt 기본 분석
#   python main.py today.txt          → 파일 지정 (기본 xlsx파일만 출력)
#   python main.py a.txt b.txt        → 여러 파일
#   python main.py logs/              → 폴더 안 txt 전부 분석
#   python main.py today.txt --all    → XLSX + JSON + HTML 전부 출력

import sys
from pathlib import Path

# qa_tools.py 가 있는 폴더를 Python 경로에 추가
# → main.py 와 같은 폴더에 있는 qa_tools.py 를 import 할 수 있게 됨
sys.path.insert(0, str(Path(__file__).parent))

import qa_tools


def 분석_실행(파일명, 옵션):
    """로그 파일 하나를 분석해서 다중 형식으로 저장"""
    print(f"\n[{파일명}] 분석 시작...")
    print("━" * 30)

    전체로그 = qa_tools.로그_읽기(str(파일명))
    if not 전체로그:
        return

    에러로그 = qa_tools.에러_필터링(전체로그)
    버그목록 = [qa_tools.버그정보_추출(로그) for 로그 in 에러로그]
    중복결과 = qa_tools.중복_감지(버그목록)
    비교결과 = qa_tools.히스토리_비교(버그목록)

    error수   = sum(1 for 로그 in 전체로그 if "ERROR"   in 로그)
    warning수 = sum(1 for 로그 in 전체로그 if "WARNING" in 로그)
    info수    = sum(1 for 로그 in 전체로그 if "INFO"    in 로그)
    버그ID목록 = [버그["버그ID"] for 버그 in 버그목록]

    # 통계 출력
    print(f"총 로그 수    : {len(전체로그)}건")
    print(f"ERROR         : {error수}건 ")
    print(f"WARNING       : {warning수}건 ")
    print(f"INFO          : {info수}건 ")
    print(f"버그 ID 목록  : {버그ID목록}")
    print("━" * 30)

    # 중복 / 변경 사항 출력
    if 중복결과:
        print("[WARN]  중복 발생 버그:")
        for id, 횟수 in 중복결과.items():
            print(f"   {id} → {횟수}회 발생")
    else:
        print("중복 버그 없음")

    print("━" * 30)

    if 비교결과["신규"]:
        print(f"[NEW] 신규 버그: {비교결과['신규']}")
    if 비교결과["해결"]:
        print(f"[RESOLVED] 해결 버그: {비교결과['해결']}")
    if not 비교결과["신규"] and not 비교결과["해결"]:
        print("변경 사항 없음")

    print("━" * 30)

    # 옵션에 따라 저장
    if 옵션 in ["--xlsx", "--all"] or not 옵션.startswith("--"):
        경로 = qa_tools.엑셀_저장(버그목록, 전체로그, 비교결과, 중복결과)
        print(f"[XLSX] 저장 완료: {경로}")

    if 옵션 in ["--json", "--all"]:
        경로 = qa_tools.리포트_JSON_저장(버그목록, 전체로그, 비교결과, 중복결과)
        print(f"[JSON] 저장 완료: {경로}")

    if 옵션 in ["--html", "--all"]:
        경로 = qa_tools.리포트_HTML_저장(버그목록, 전체로그, 비교결과, 중복결과)
        print(f"[HTML] 저장 완료: {경로}")


# ── 인자 파싱 ──
파일목록 = []
옵션 = "--xlsx"

for 인자 in sys.argv[1:]:
    if 인자.startswith("--"):
        옵션 = 인자
    else:
        파일목록.append(인자)

if not 파일목록:
    print("[ERROR] 파일을 지정하지 않아 기본 파일(bug_log.txt)사용")
    파일목록 = ["bug_log.txt"]
    print("")
    print("기존 사용법:")
    print("  python main.py bug_log.txt          → XLSX만")
    print("  python main.py bug_log.txt --all    → XLSX + JSON + HTML")
    print("  python main.py logs/                → 폴더 안 전부")

for 파일명 in 파일목록:
    인자_경로 = Path(파일명)
    if 인자_경로.is_dir():
        파일들 = list(인자_경로.glob("*.txt")) + list(인자_경로.glob("*.log"))
        if not 파일들:
            print("[ERROR] 폴더 안에 txt/log 파일이 없어요:", 인자_경로)
        else:
            print(f"폴더 분석 시작: {인자_경로} ({len(파일들)}개 파일)")
            for 파일 in 파일들:
                분석_실행(파일, 옵션)
    else:
        분석_실행(파일명, 옵션)