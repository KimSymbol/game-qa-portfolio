# 역할: 버그 데이터를 다양한 형식의 리포트로 생성하는 실행 파일
#
# 실행 방법:
#   python main.py bugs.csv                → 엑셀만 생성 (기본)
#   python main.py bugs.csv --all          → 엑셀 + JSON + HTML 전부
#   python main.py bugs.csv --json         → JSON만
#   python main.py bugs.csv --html         → HTML만
#   python main.py bugs.csv --excel
#   python main.py bugs.pdf --pdf          → pdf만 

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from common.logger import 로거_생성

import reporter

log = 로거_생성("excel-reporter")

def 리포트_실행(파일명, 옵션):
    """파일 하나를 분석해서 지정된 형식으로 저장"""
    log.info(f"리포트 생성 시작: {파일명}")
    print(f"\n[{파일명}] 리포트 생성 시작...")
    print("━" * 30)

    df = reporter.데이터_읽기(파일명)
    if df is None:
        log.error(f"데이터 읽기 실패: {파일명}")
        return

    # 통계 출력
    총버그 = len(df)
    해결   = len(df[df["상태"] == "해결"])
    해결률 = round(해결 / 총버그 * 100, 1) if 총버그 > 0 else 0

    print(f"총 버그 수  : {총버그}건")
    print(f"해결률      : {해결률}%")
    print("━" * 30)

    log.info(f"통계 - 총 {총버그}건 / 해결률 {해결률}%")

    # 옵션에 따라 출력 형식 결정
    생성된파일 = []

    try:
        if 옵션 in ["--excel", "--all"] or not 옵션.startswith("--"):
            경로 = reporter.리포트_생성(df)
            print(f"[XLSX] 저장 완료: {경로}")
            log.info(f"XLSX 저장 완료: {경로}")
            생성된파일.append(경로)

        if 옵션 in ["--json", "--all"]:
            경로 = reporter.리포트_생성_JSON(df)
            print(f"[JSON] 저장 완료: {경로}")
            log.info(f"JSON 저장 완료: {경로}")
            생성된파일.append(경로)

        if 옵션 in ["--html", "--all"]:
            경로 = reporter.리포트_생성_HTML(df)
            print(f"[HTML] 저장 완료: {경로}")
            log.info(f"HTML 저장 완료: {경로}")
            생성된파일.append(경로)

        if 옵션 in ["--pdf", "--all"]:
            경로 = reporter.리포트_생성_PDF(df)
            print(f"[PDF] 저장 완료: {경로}")
            log.info(f"PDF 저장 완료: {경로}")
            생성된파일.append(경로)

    except Exception as e:
        log.error(f"리포트 생성 실패: {type(e).__name__}: {e}")
        print(f"[ERROR] 리포트 생성 중 에러: {e}")
        return

    log.info(f"전체 완료 - {len(생성된파일)}개 파일 생성")


# ── 인자 파싱 ──
파일목록 = []
옵션 = "--excel"

for 인자 in sys.argv[1:]:
    if 인자.startswith("--"):
        옵션 = 인자
    else:
        파일목록.append(인자)

if not 파일목록:
    print("[ERROR] 파일을 지정해주세요")
    print("")
    print("사용법:")
    print("  python main.py bugs.csv             → 엑셀만 생성")
    print("  python main.py bugs.csv --all       → 엑셀 + JSON + HTML + PDF")
    print("  python main.py bugs.csv --json      → JSON만")
    print("  python main.py bugs.csv --html      → HTML만")
    print("  python main.py bugs.csv --pdf       → PDF만")
    log.warning("실행 인자 없음")

else:
    log.info(f"실행 시작 - 옵션: {옵션} / 파일: {파일목록}")
    for 파일명 in 파일목록:
        인자_경로 = Path(파일명)
        if 인자_경로.is_dir():
            csv목록 = list(인자_경로.glob("*.csv"))
            xlsx목록 = list(인자_경로.glob("*.xlsx"))
            tsv목록 = list(인자_경로.glob("*.tsv"))
            json목록 = list(인자_경로.glob("*.json"))
            전체 = csv목록 + xlsx목록 + tsv목록 + json목록

            if not 전체:
                print("[ERROR] 폴더 안에 지원하는 파일이 없어요:", 인자_경로)
                log.warning(f"빈 폴더: {인자_경로}")
            else:
                print(f"폴더 분석 시작: {인자_경로} ({len(전체)}개 파일)")
                log.info(f"폴더 분석: {인자_경로} ({len(전체)}개)")
                for 파일 in 전체:
                    리포트_실행(str(파일), 옵션)
        else:
            리포트_실행(파일명, 옵션)