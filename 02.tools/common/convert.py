# 역할: 외부 TC/버그 파일을 내부 형식으로 변환
#
# 실행 방법:
#   python common/convert.py 파일.csv                       → 자동 감지 변환
#   python common/convert.py 파일.csv --map 매핑이름         → 매핑 지정
#   python common/convert.py 파일.csv --preview              → 미리보기 (저장 안 함)
#   python common/convert.py 파일.csv --generate 매핑이름    → 매핑 초안 자동 생성
#   python common/convert.py --validate                      → 매핑 설정 검증
#   python common/convert.py --list                          → 매핑 목록 조회

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from common.logger import 로거_생성
from common.column_mapper import (
    변환_저장, 매핑_목록_조회, 매핑_자동생성,
    변환_미리보기, 매핑_검증
)

log = 로거_생성("converter")


# ── 매핑 목록 조회 ──
if "--list" in sys.argv:
    print("사용 가능한 매핑 목록:")
    print("━" * 50)
    목록 = 매핑_목록_조회()
    for 이름, 설명 in 목록.items():
        print(f"  {이름:20s} {설명}")
    print("━" * 50)
    print("사용법: python common/convert.py 파일.csv --map 매핑이름")
    sys.exit(0)


# ── 매핑 검증 ──
if "--validate" in sys.argv:
    print("매핑 설정 검증 시작...")
    print("━" * 50)

    결과 = 매핑_검증()
    if 결과 is None:
        print("[ERROR] column_map.json 로딩 실패")
        sys.exit(1)

    pass수 = 0
    warn수 = 0
    fail수 = 0

    for 이름, 정보 in 결과.items():
        상태 = 정보["상태"]
        접두사 = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}[상태]

        print(f"{접두사} {이름}")

        if 상태 == "PASS":
            pass수 += 1
        elif 상태 == "WARN":
            warn수 += 1
            for 메시지 in 정보["메시지"]:
                print(f"       {메시지}")
        elif 상태 == "FAIL":
            fail수 += 1
            for 메시지 in 정보["메시지"]:
                print(f"       {메시지}")

    print("━" * 50)
    print(f"검증 완료: {pass수}개 정상 / {warn수}개 경고 / {fail수}개 실패")
    sys.exit(0)


# ── 인자 파싱 ──
파일목록 = []
매핑이름 = None
출력폴더 = None
미리보기모드 = False
생성모드 = False
생성매핑이름 = None

i = 1
while i < len(sys.argv):
    인자 = sys.argv[i]

    if 인자 == "--map" and i + 1 < len(sys.argv):
        매핑이름 = sys.argv[i + 1]
        i += 1
    elif 인자 == "--output" and i + 1 < len(sys.argv):
        출력폴더 = sys.argv[i + 1]
        i += 1
    elif 인자 == "--preview":
        미리보기모드 = True
    elif 인자 == "--generate" and i + 1 < len(sys.argv):
        생성모드 = True
        생성매핑이름 = sys.argv[i + 1]
        i += 1
    elif not 인자.startswith("--"):
        파일목록.append(인자)

    i += 1


# ── 실행 ──
if not 파일목록:
    print("[ERROR] 파일을 지정해주세요")
    print("")
    print("사용법:")
    print("  python common/convert.py 파일.csv                      → 자동 감지 변환")
    print("  python common/convert.py 파일.csv --map 매핑이름        → 매핑 지정")
    print("  python common/convert.py 파일.csv --preview             → 미리보기")
    print("  python common/convert.py 파일.csv --generate 매핑이름   → 매핑 초안 생성")
    print("  python common/convert.py --validate                     → 매핑 설정 검증")
    print("  python common/convert.py --list                         → 매핑 목록")

else:
    for 파일명 in 파일목록:

        # ── 매핑 자동 생성 모드 ──
        if 생성모드:
            print(f"[{파일명}] 매핑 초안 생성 중...")
            print("━" * 50)

            try:
                결과 = 매핑_자동생성(파일명, 생성매핑이름)
                if 결과:
                    print(f"외부 파일 컬럼 감지 ({len(결과['컬럼목록'])}개):")
                    print()

                    # 자동 추천 결과
                    if 결과["추천됨"]:
                        print(f"자동 추천 완료 ({len(결과['추천됨'])}개):")
                        for 외부, 내부 in 결과["추천됨"]:
                            print(f"  {외부:20s} → {내부}")

                    if 결과["미추천"]:
                        print(f"\n미매칭 ({len(결과['미추천'])}개) — 직접 입력 필요:")
                        for 컬럼 in 결과["미추천"]:
                            print(f"  {컬럼:20s} → ???")

                    print("━" * 50)
                    print(f"매핑 '{결과['매핑이름']}' 초안이 column_map.json 에 추가되었습니다.")
                    print()
                    print("다음 단계:")
                    if 결과["미추천"]:
                        print("  1. common/column_map.json 열기")
                        print(f"  2. '{결과['매핑이름']}' 의 빈 값에 내부 컬럼명 입력")
                        print(f"  3. python common/convert.py --validate")
                        print(f"  4. python common/convert.py {파일명} --map {결과['매핑이름']} --preview")
                        print(f"  5. python common/convert.py {파일명} --map {결과['매핑이름']}")
                    else:
                        print("  자동 추천이 완료되었습니다. 확인 후 바로 사용 가능:")
                        print(f"  1. python common/convert.py {파일명} --map {결과['매핑이름']} --preview")
                        print(f"  2. python common/convert.py {파일명} --map {결과['매핑이름']}")
                else:
                    print("[ERROR] 매핑 생성 실패")
            except Exception as e:
                log.error(f"매핑 생성 실패: {type(e).__name__}: {e}")
                print(f"[ERROR] 매핑 생성 실패: {e}")

        # ── 미리보기 모드 ──
        elif 미리보기모드:
            try:
                변환_미리보기(파일명, 매핑이름)
            except Exception as e:
                log.error(f"미리보기 실패: {type(e).__name__}: {e}")
                print(f"[ERROR] 미리보기 실패: {e}")

        # ── 일반 변환 모드 ──
        else:
            print(f"[{파일명}] 변환 시작...")
            print("━" * 50)

            try:
                결과 = 변환_저장(파일명, 매핑이름, 출력폴더=출력폴더)
                if 결과:
                    print(f"변환 완료! ({결과['건수']}건)")
                    print(f"  CSV : {결과['csv']}")
                    print(f"  XLSX: {결과['xlsx']}")
                    print("━" * 50)
                    print("바로 사용 가능한 명령어:")
                    print(f"  python 02.data-validator/main.py {결과['csv']}")
                    print(f"  python 03.md-report-gen/main.py {결과['csv']}")
                    print(f"  python 04.excel-reporter/main.py {결과['csv']} --all")
                else:
                    print("[ERROR] 변환 실패")
            except Exception as e:
                log.error(f"변환 실패: {type(e).__name__}: {e}")
                print(f"[ERROR] 변환 실패: {e}")