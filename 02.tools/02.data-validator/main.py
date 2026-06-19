# 역할: CSV 파일의 데이터 무결성을 자동으로 검증하는 실행 파일
# validator.py 의 함수들을 호출해서 검사 → 출력 → 엑셀 저장까지 진행
#
# 실행 방법:
#   python main.py bugs.csv                    → 파일 지정
#   python main.py a.csv b.csv                 → 여러 파일
#   python main.py data/                       → 폴더 안 csv 전부 검사

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from common.logger import 로거_생성
log = 로거_생성("data-validator")

import validator


def 검증_시작(파일명, 옵션):
    """파일 하나를 검증해서 결과 출력 + 다중 형식 저장"""
    print(f"\n📋 [{파일명}] 데이터 검증 시작...")
    print("━" * 30)
    log.info(f"검증 시작: {파일명} (옵션: {옵션})")

    try:
        결과 = validator.검증_실행(파일명, 옵션)
        if 결과 is None:
            log.error(f"검증 실패: {파일명}")
            return
    except Exception as e:
        log.error(f"검증 중 에러: {type(e).__name__}: {e}")
        print(f"❌ 검증 실패: {e}")
        return

    print("━" * 30)

    오류수 = len(결과["오류목록"])
    if 오류수 == 0:
        print("🎉 문제 없음! 데이터가 깨끗해요!")
        log.info(f"검증 통과: {파일명}")
    else:
        print(f"⚠️  총 {오류수}건의 문제 발견")
        log.warning(f"오류 {오류수}건 발견: {파일명}")

    print(f"📁 생성된 리포트: {len(결과['리포트'])}개")
    log.info(f"리포트 {len(결과['리포트'])}개 생성 완료")


# ── 인자 파싱 ──
파일목록 = []
옵션 = "--xlsx"

for 인자 in sys.argv[1:]:
    if 인자.startswith("--"):
        옵션 = 인자
    else:
        파일목록.append(인자)

if not 파일목록:
    print("❌ 파일을 지정해주세요")
    print("")
    print("사용법:")
    print("  python main.py bugs.csv             → XLSX만 생성")
    print("  python main.py bugs.csv --all       → XLSX + JSON + HTML")
    print("  python main.py bugs.csv --json      → JSON만")
    print("  python main.py bugs.csv --html      → HTML만")
    log.warning("실행 인자 없음")

else:
    log.info(f"실행 시작 - 옵션: {옵션} / 파일: {파일목록}")
    for 파일명 in 파일목록:
        인자_경로 = Path(파일명)
        if 인자_경로.is_dir():
            파일들 = list(인자_경로.glob("*.csv")) + list(인자_경로.glob("*.xlsx"))
            if not 파일들:
                print("❌ 폴더 안에 csv/xlsx 파일이 없어요:", 인자_경로)
                log.warning(f"빈 폴더: {인자_경로}")
            else:
                print(f"📂 폴더 검증 시작: {인자_경로} ({len(파일들)}개 파일)")
                log.info(f"폴더 검증: {인자_경로} ({len(파일들)}개)")
                for 파일 in 파일들:
                    검증_시작(str(파일), 옵션)
        else:
            검증_시작(파일명, 옵션)