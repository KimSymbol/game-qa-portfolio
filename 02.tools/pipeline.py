# 역할: QA 도구 5개를 순차적으로 자동 실행하는 통합 파이프라인
# 위치: 02.tools/pipeline.py
#
# 실행 흐름:
#   01.test-data-gen   → 더미 데이터 생성
#         ↓
#   02.data-validator  → 데이터 무결성 검증
#         ↓
#   03.md-report-gen   → 마크다운 버그 리포트
#         ↓
#   04.excel-reporter  → 엑셀/HTML/JSON/PDF 리포트
#         ↓
#   05.log-analyzer    → 로그 분석 리포트
#
# 사용법:
#   python pipeline.py                          → 기본 실행
#   python pipeline.py --all                    → 모든 출력 형식
#   python pipeline.py --skip-gen               → 데이터 생성 건너뛰기
#   python pipeline.py --count 50               → 데이터 건수 지정
#   python pipeline.py --data bugs              → 특정 데이터만
#   python pipeline.py --open                   → 완료 후 결과 폴더 오픈
#
# 옵션 조합 가능:
#   python pipeline.py --all --count 50 --open

import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# 02.tools 폴더를 Python 경로에 추가
기준경로 = Path(__file__).parent
sys.path.insert(0, str(기준경로))

from common.logger import 로거_생성

# 파이프라인 전용 로거
log = 로거_생성("pipeline")


# ────────────────────────────────────────
# 옵션 파싱
# ────────────────────────────────────────
def 옵션_파싱():
    """커맨드라인 인자 파싱"""
    옵션 = {
        "all"       : False,
        "skip_gen"  : False,
        "skip_tc"   : False,
        "count"     : None,
        "data"      : "all",
        "open"      : False,
        "start_from": 0,        # ← 추가
    }

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        인자 = args[i]

        if 인자 == "--all":
            옵션["all"] = True
        elif 인자 == "--skip-gen":
            옵션["skip_gen"] = True
        elif 인자 == "--skip-tc":
            옵션["skip_tc"] = True
        elif 인자 == "--open":
            옵션["open"] = True
        elif 인자 == "--count" and i + 1 < len(args):
            try:
                옵션["count"] = int(args[i + 1])
                i += 1
            except ValueError:
                print(f"[WARN]  --count 뒤에 숫자가 와야 해요")
        elif 인자 == "--data" and i + 1 < len(args):
            옵션["data"] = args[i + 1]
            i += 1
        elif 인자 == "--start-from" and i + 1 < len(args):
            try:
                단계 = int(args[i + 1])
                if 0 <= 단계 <= 5:
                    옵션["start_from"] = 단계
                else:
                    print(f"[WARN]  --start-from 는 0~5 사이의 숫자여야 해요")
                i += 1
            except ValueError:
                print(f"[WARN]  --start-from 뒤에 숫자가 와야 해요")
        elif 인자 in ["-h", "--help"]:
            도움말_출력()
            sys.exit(0)
        else:
            print(f"[WARN]  알 수 없는 옵션: {인자}")

        i += 1

    return 옵션

# ────────────────────────────────────────
# 도움말
# ────────────────────────────────────────
def 도움말_출력():
    """사용법 안내"""
    print("""
QA 도구 자동 파이프라인

사용법:
  python pipeline.py [옵션]

옵션:
  --all              모든 출력 형식 생성 (xlsx + json + html + pdf)
  --skip-tc          TC 생성 건너뛰기
  --skip-gen         테스트 데이터 생성 건너뛰기
  --start-from N     N 단계부터 시작 (0~5)
  --count N          생성할 데이터 건수 지정
  --data 종류        특정 데이터만 처리 (bugs, testcases, items, all)
  --open             완료 후 결과 폴더 자동 오픈
  -h, --help         도움말 표시

단계 번호:
  0: TC 생성 (tc-generator)
  1: 데이터 생성 (test-data-gen)
  2: 데이터 검증 (data-validator)
  3: 마크다운 리포트 (md-report-gen)
  4: 엑셀 리포트 (excel-reporter)
  5: 로그 분석 (log-analyzer)

예시:
  python pipeline.py                          → 처음부터 끝까지
  python pipeline.py --start-from 2           → 단계 2부터 시작
  python pipeline.py --start-from 3 --all     → 단계 3부터 모든 형식
  python pipeline.py --skip-gen --all         → 데이터 생성 건너뛰고 모든 형식
  python pipeline.py --all --open             → 모든 형식 + 폴더 자동 오픈
""")


# ────────────────────────────────────────
# 단계별 실행 함수
# ────────────────────────────────────────
def 명령_실행(설명, 명령어목록):
    """
    subprocess로 명령어 실행
    터미널에 출력도 그대로 보여주고 결과 반환
    """
    print(f"\n{'━' * 50}")
    print(f"{설명}")
    print(f"   명령: {' '.join(명령어목록)}")
    print(f"{'━' * 50}")

    log.info(f"단계 시작: {설명}")

    try:
        결과 = subprocess.run(
            명령어목록,
            cwd=str(기준경로),
            check=False
        )
        if 결과.returncode == 0:
            log.info(f"단계 완료: {설명}")
            return True
        else:
            log.error(f"단계 실패: {설명} (종료 코드: {결과.returncode})")
            return False
    except Exception as e:
        log.error(f"실행 중 에러: {설명} - {type(e).__name__}: {e}")
        print(f"실행 실패: {e}")
        return False


def 단계0_TC생성(옵션):
    """⓪ tc-generator → 사양 기반 TC 자동 생성"""
    명령 = [sys.executable, "06.tc-generator/main.py"]
    return 명령_실행("[단계 0] TC 자동 생성 (ISTQB 기법)", 명령)


def 단계1_데이터생성(옵션):
    """① test-data-gen → 더미 데이터 생성"""
    명령 = [sys.executable, "01.test-data-gen/main.py"]

    # --data 옵션 (특정 데이터만)
    if 옵션["data"] != "all":
        명령.append(옵션["data"])

    # --count 옵션
    if 옵션["count"]:
        명령.append(str(옵션["count"]))

    return 명령_실행("[단계 1] 테스트 데이터 생성", 명령)


def 단계2_데이터검증(옵션):
    """② data-validator → 데이터 무결성 검증"""
    파일경로 = "01.test-data-gen/결과/bugs_latest.csv"

    명령 = [sys.executable, "02.data-validator/main.py", 파일경로]

    if 옵션["all"]:
        명령.append("--all")

    return 명령_실행("[단계 2] 데이터 무결성 검증", 명령)


def 단계3_마크다운리포트(옵션):
    """③ md-report-gen → 마크다운 버그 리포트"""
    파일경로 = "01.test-data-gen/결과/testcases_latest.csv"

    명령 = [sys.executable, "03.md-report-gen/main.py", 파일경로]

    return 명령_실행("[단계 3] 마크다운 버그 리포트 생성", 명령)


def 단계4_엑셀리포트(옵션):
    """④ excel-reporter → 다양한 형식의 리포트"""
    # md-report-gen 에서 만든 bugs_latest.csv 사용
    파일경로 = "03.md-report-gen/결과/bugs_latest.csv"

    명령 = [sys.executable, "04.excel-reporter/main.py", 파일경로]

    if 옵션["all"]:
        명령.append("--all")

    return 명령_실행("[단계 4] 엑셀 리포트 생성", 명령)


def 단계5_로그분석(옵션):
    """⑤ log-analyzer → 로그 분석 리포트"""
    파일경로 = "01.test-data-gen/결과/logs_latest.txt"

    명령 = [sys.executable, "05.log-analyzer/main.py", 파일경로]

    if 옵션["all"]:
        명령.append("--all")

    return 명령_실행("[단계 5] 로그 분석", 명령)


# ────────────────────────────────────────
# 결과 폴더 오픈
# ────────────────────────────────────────
def 결과폴더_오픈():
    """
    OS에 맞게 결과 폴더 자동 오픈
    - Windows : explorer
    - Mac     : open
    - Linux   : xdg-open
    """
    print("\n결과 폴더 자동 오픈 중...")
    log.info("결과 폴더 자동 오픈")

    폴더목록 = [
        기준경로 / "01.test-data-gen" / "결과",
        기준경로 / "02.data-validator" / "결과",
        기준경로 / "03.md-report-gen" / "결과",
        기준경로 / "04.excel-reporter" / "결과",
        기준경로 / "05.log-analyzer" / "결과",
    ]

    OS이름 = platform.system()

    for 폴더 in 폴더목록:
        if not 폴더.exists():
            continue
        try:
            if OS이름 == "Windows":
                subprocess.run(["explorer", str(폴더)])
            elif OS이름 == "Darwin":
                subprocess.run(["open", str(폴더)])
            elif OS이름 == "Linux":
                subprocess.run(["xdg-open", str(폴더)])
        except Exception as e:
            log.warning(f"폴더 오픈 실패: {폴더} - {e}")


# ────────────────────────────────────────
# 메인 실행
# ────────────────────────────────────────
def 파이프라인_실행():
    """전체 파이프라인 순차 실행"""
    시작시간 = datetime.now()

    print("\n" + "=" * 50)
    print("QA 도구 자동 파이프라인 시작")
    print(f"시작 시각: {시작시간.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 옵션 파싱
    옵션 = 옵션_파싱()
    시작단계 = 옵션.get("start_from", 0)

    if 시작단계 > 0:
        print(f"단계 {시작단계} 부터 시작합니다")

    log.info(f"파이프라인 시작 - 옵션: {옵션}")

    # 진행 상태 추적
    결과 = {
        "성공": [],
        "실패": [],
        "건너뜀": [],
    }

    # ── 단계 0: TC 생성 ──
    if 시작단계 > 0 or 옵션["skip_tc"]:
        print("\n [SKIP] 단계 0: TC 생성 건너뛰기")
        결과["건너뜀"].append("단계 0: TC 생성")
        log.info("단계 0 건너뜀")
    else:
        if 단계0_TC생성(옵션):
            결과["성공"].append("단계 0: TC 생성")
        else:
            결과["실패"].append("단계 0: TC 생성")

    # ── 단계 1: 데이터 생성 ──
    if 시작단계 > 1 or 옵션["skip_gen"]:
        print("\n [단계 1] 데이터 생성 건너뛰기")
        결과["건너뜀"].append("단계 1: 데이터 생성")
        log.info("단계 1 건너뜀")
    else:
        if 단계1_데이터생성(옵션):
            결과["성공"].append("단계 1: 데이터 생성")
        else:
            결과["실패"].append("단계 1: 데이터 생성")
            print("[FAIL] 데이터 생성 실패 → 파이프라인 중단")
            log.error("단계 1 실패로 파이프라인 중단")
            _최종결과_출력(결과, 시작시간)
            return

    # ── 단계 2: 데이터 검증 ──
    if 시작단계 > 2:
        print("\n [단계 2] 데이터 검증 건너뛰기")
        결과["건너뜀"].append("단계 2: 데이터 검증")
        log.info("단계 2 건너뜀")
    else:
        if 단계2_데이터검증(옵션):
            결과["성공"].append("단계 2: 데이터 검증")
        else:
            결과["실패"].append("단계 2: 데이터 검증")

    # ── 단계 3: 마크다운 리포트 ──
    if 시작단계 > 3:
        print("\n [단계 3] 마크다운 리포트 건너뛰기")
        결과["건너뜀"].append("단계 3: 마크다운 리포트")
        log.info("단계 3 건너뜀")
    else:
        if 단계3_마크다운리포트(옵션):
            결과["성공"].append("단계 3: 마크다운 리포트")
        else:
            결과["실패"].append("단계 3: 마크다운 리포트")

    # ── 단계 4: 엑셀 리포트 ──
    if 시작단계 > 4:
        print("\n [단계 4] 엑셀 리포트 건너뛰기")
        결과["건너뜀"].append("단계 4: 엑셀 리포트")
        log.info("단계 4 건너뜀")
    else:
        if 단계4_엑셀리포트(옵션):
            결과["성공"].append("단계 4: 엑셀 리포트")
        else:
            결과["실패"].append("단계 4: 엑셀 리포트")

    # ── 단계 5: 로그 분석 ──
    if 시작단계 > 5:
        print("\n [단계 5] 로그 분석 건너뛰기")
        결과["건너뜀"].append("단계 5: 로그 분석")
        log.info("단계 5 건너뜀")
    else:
        if 단계5_로그분석(옵션):
            결과["성공"].append("단계 5: 로그 분석")
        else:
            결과["실패"].append("단계 5: 로그 분석")

    # ── 최종 결과 출력 ──
    _최종결과_출력(결과, 시작시간)

    # ── 결과 폴더 자동 오픈 ──
    if 옵션["open"]:
        결과폴더_오픈()


def _최종결과_출력(결과, 시작시간):
    """파이프라인 종료 후 결과 요약 출력"""
    종료시간 = datetime.now()
    걸린시간 = (종료시간 - 시작시간).total_seconds()

    print("\n" + "=" * 50)
    print("파이프라인 실행 결과")
    print("=" * 50)
    print(f"종료 시각: {종료시간.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"걸린 시간: {걸린시간:.1f}초")
    print()
    print(f"[PASS] {len(결과['성공'])}건")
    for 단계 in 결과["성공"]:
        print(f"   ✓ {단계}")

    if 결과["건너뜀"]:
        print(f"\n [SKIP] 건너뜀: {len(결과['건너뜀'])}건")
        for 단계 in 결과["건너뜀"]:
            print(f"   - {단계}")

    if 결과["실패"]:
        print(f"\n[FAIL] 실패: {len(결과['실패'])}건")
        for 단계 in 결과["실패"]:
            print(f"   ✗ {단계}")

    print("=" * 50)

    # 결과 폴더 경로 안내
    print("\n결과 폴더:")
    print("   01.test-data-gen/결과/")
    print("   02.data-validator/결과/")
    print("   03.md-report-gen/결과/")
    print("   04.excel-reporter/결과/")
    print("   05.log-analyzer/결과/")

    log.info(f"파이프라인 종료 - 성공: {len(결과['성공'])} / 실패: {len(결과['실패'])} / 시간: {걸린시간:.1f}초")


# 실행
if __name__ == "__main__":
    파이프라인_실행()