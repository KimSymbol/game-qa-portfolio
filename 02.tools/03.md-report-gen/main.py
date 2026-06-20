
# 역할: 테스트 케이스 파일을 읽어 마크다운 버그 리포트를 생성하는 실행 파일
# md_generator.py 의 함수들을 호출해서 분석 → 마크다운 저장 → bugs.csv 저장
#
# 실행 방법:
#   python main.py                          → testcases.csv 기본 분석
#   python main.py testcases.xlsx          → xlsx 파일 분석
#   python main.py a.csv b.xlsx            → 여러 파일 분석
#   python main.py data/                   → 폴더 안 csv/xlsx 전부 분석

# main.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from common.logger import 로거_생성
log = 로거_생성("md-report-gen")

import md_generator


def 리포트_실행(파일명):
    """파일 하나를 분석해서 마크다운 리포트 + bugs.csv 생성"""
    print(f"\n[{파일명}] 리포트 생성 시작...")
    print("━" * 30)
    log.info(f"리포트 생성 시작: {파일명}")

    try:
        결과 = md_generator.리포트_생성(파일명)
        if 결과 is None:
            log.error(f"리포트 생성 실패: {파일명}")
            return
    except Exception as e:
        log.error(f"리포트 생성 중 에러: {type(e).__name__}: {e}")
        print(f"[ERROR] 리포트 생성 실패: {e}")
        return

    print("━" * 30)
    print(f"개별 리포트: {len(결과['개별'])}건")
    print(f"통합 리포트: {결과['통합']}")
    print(f"bugs.csv: {결과['csv']}")
    print("━" * 30)
    print("생성 완료!")
    print()
    print("다음 단계:")
    print(f"   excel-reporter 로 엑셀 리포트 생성:")
    print(f"   python 04.excel-reporter/main.py {결과['csv']}")

    log.info(f"개별 리포트 {len(결과['개별'])}건 생성")
    log.info(f"통합 리포트 생성: {결과['통합']}")
    log.info(f"bugs.csv 생성: {결과['csv']}")


# ── 커맨드라인 인자에 따라 실행 방식 결정 ──
if len(sys.argv) == 1:
    print("[ERROR] 파일을 지정해주세요")
    print("")
    print("사용법:")
    print("  python main.py testcases.csv")
    print("  python main.py 01.test-data-gen/결과/testcases_2026-06-17_*.csv")
    print("  python main.py data/")
    log.warning("실행 인자 없음")

else:
    log.info(f"실행 시작 - 인자: {sys.argv[1:]}")
    인자 = Path(sys.argv[1])

    if 인자.is_dir():
        파일목록 = list(인자.glob("*.csv")) + list(인자.glob("*.xlsx"))
        if not 파일목록:
            print("[ERROR] 폴더 안에 csv/xlsx 파일이 없어요:", 인자)
            log.warning(f"빈 폴더: {인자}")
        else:
            print(f"폴더 분석 시작: {인자} ({len(파일목록)}개 파일)")
            log.info(f"폴더 분석: {인자} ({len(파일목록)}개)")
            for 파일 in 파일목록:
                리포트_실행(str(파일))
    else:
        for 파일명 in sys.argv[1:]:
            리포트_실행(파일명)