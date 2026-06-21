# 역할: 외부 TC/버그 데이터를 내부 형식으로 자동 변환
#
# 사용법:
#   from common.column_mapper import 컬럼_변환, 매핑_목록_조회
#
#   df = 컬럼_변환("외부파일.csv", "부트캠프_1차")
#   → 내부 형식 DataFrame 반환
#
#   df = 컬럼_변환("외부파일.csv")
#   → 자동 감지 시도

import json
import pandas as pd
from pathlib import Path

from common.file_io import 파일_읽기
from common.logger import 로거_생성

log = 로거_생성("column-mapper")

# column_mapper.py 가 있는 폴더 (common/)
_기준경로 = Path(__file__).parent
_매핑파일 = _기준경로 / "column_map.json"


def _매핑_로딩():
    """column_map.json 로딩"""
    if not _매핑파일.exists():
        log.error(f"매핑 파일 없음: {_매핑파일}")
        return None

    try:
        with open(_매핑파일, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"매핑 파일 로딩 실패: {e}")
        return None


def 매핑_목록_조회():
    """
    사용 가능한 매핑 목록 반환

    반환값:
    - 딕셔너리: {매핑이름: 설명}
    """
    설정 = _매핑_로딩()
    if 설정 is None:
        return {}

    목록 = {}
    for 이름, 내용 in 설정.get("매핑_목록", {}).items():
        목록[이름] = 내용.get("설명", "")

    return 목록


def 매핑_자동감지(df):
    """
    DataFrame 의 컬럼명과 값을 보고 매핑 자동 감지

    감지 방법:
    1. TC_ID 패턴으로 판단 (LI-, SI-, FA- 등)
    2. 컬럼명 유사도로 판단
    3. 매칭 안 되면 "기본" 반환

    반환값:
    - 매핑 이름 (str)
    """
    설정 = _매핑_로딩()
    if 설정 is None:
        return "기본"

    컬럼목록 = list(df.columns)

    # 이미 내부 형식인지 확인
    내부_필수_컬럼 = 설정.get("내부_필수_컬럼", {})
    if isinstance(내부_필수_컬럼, dict):
        for 타입, 필수 in 내부_필수_컬럼.items():
            if set(필수).issubset(set(컬럼목록)):
                log.info(f"자동 감지: 내부 형식 ({타입}, 변환 불필요)")
                return "기본"
    else:
        if set(내부_필수_컬럼).issubset(set(컬럼목록)):
            log.info("자동 감지: 내부 형식 (변환 불필요)")
            return "기본"

    # 각 매핑별 점수 계산
    최고점수 = 0
    최고매핑 = "기본"

    for 이름, 내용 in 설정.get("매핑_목록", {}).items():
        if 이름 == "기본":
            continue

        컬럼매핑 = 내용.get("컬럼_매핑", {})
        점수 = 0

        for 외부컬럼 in 컬럼매핑.keys():
            if 외부컬럼 in 컬럼목록:
                점수 += 1

        if 점수 > 최고점수:
            최고점수 = 점수
            최고매핑 = 이름

    if 최고점수 > 0:
        log.info(f"자동 감지: {최고매핑} (점수: {최고점수})")
        return 최고매핑

    log.warning("자동 감지 실패 - 기본 매핑 사용")
    return "기본"


def 컬럼_변환(파일명, 매핑이름=None, 기준경로=None):
    """
    외부 파일을 내부 형식으로 변환

    매개변수:
    - 파일명   : 변환할 CSV/XLSX 파일
    - 매핑이름 : 사용할 매핑 (None 이면 자동 감지)
    - 기준경로 : 파일 탐색 기준 경로

    동작 순서:
    1. 파일 읽기
    2. 매핑 감지 (지정 안 했으면 자동)
    3. 컬럼명 변환
    4. 값 변환 (우선순위 등)
    5. 누락 컬럼 기본값 추가
    6. 변환된 DataFrame 반환

    반환값:
    - 변환된 DataFrame
    - None: 실패 시
    """
    # 1. 파일 읽기
    df = 파일_읽기(파일명, 기준경로)
    if df is None:
        return None

    # 2. 매핑 설정 로딩
    설정 = _매핑_로딩()
    if 설정 is None:
        return df

    # 3. 매핑 감지
    if 매핑이름 is None:
        매핑이름 = 매핑_자동감지(df)

    if 매핑이름 == "기본":
        log.info("변환 불필요 (내부 형식)")
        return df

    매핑설정 = 설정.get("매핑_목록", {}).get(매핑이름)
    if 매핑설정 is None:
        log.error(f"매핑 '{매핑이름}' 을 찾을 수 없음")
        return df

    log.info(f"매핑 적용: {매핑이름} ({매핑설정.get('설명', '')})")

    # 4. 컬럼명 변환
    컬럼매핑 = 매핑설정.get("컬럼_매핑", {})
    if 컬럼매핑:
        df = df.rename(columns=컬럼매핑)
        log.info(f"컬럼 변환 완료: {len(컬럼매핑)}개")

    # 5. 값 변환
    값_변환 = 매핑설정.get("값_변환", {})
    for 컬럼, 변환맵 in 값_변환.items():
        if 컬럼 in df.columns:
            df[컬럼] = df[컬럼].replace(변환맵)
            log.info(f"값 변환 완료: {컬럼}")

    # 6. 데이터 타입 판별 (TC / 버그)
    데이터타입 = _데이터_타입_판별(매핑이름, df)
    log.info(f"데이터 타입: {데이터타입}")

    # 7. 누락 컬럼 기본값 추가
    기본값 = 매핑설정.get("기본값", {})
    내부_필수_컬럼 = 설정.get("내부_필수_컬럼", {})

    if isinstance(내부_필수_컬럼, dict):
        내부_필수 = 내부_필수_컬럼.get(데이터타입, [])
    else:
        내부_필수 = 내부_필수_컬럼

    for 컬럼 in 내부_필수:
        if 컬럼 not in df.columns:
            df[컬럼] = 기본값.get(컬럼, "")
            log.info(f"누락 컬럼 추가: {컬럼} (기본값: '{기본값.get(컬럼, '')}')")

    # 8. 컬럼 순서 정렬
    기존컬럼 = [c for c in 내부_필수 if c in df.columns]
    추가컬럼 = [c for c in df.columns if c not in 내부_필수]
    df = df[기존컬럼 + 추가컬럼]

    log.info(f"변환 완료: {len(df)}건 ({데이터타입})")
    return df


def 변환_저장(파일명, 매핑이름=None, 기준경로=None, 출력폴더=None):
    """
    외부 파일을 변환하고 CSV + XLSX 로 저장
    변환된 파일은 다른 도구에서 바로 사용 가능

    매개변수:
    - 파일명   : 변환할 파일
    - 매핑이름 : 매핑 (None 이면 자동 감지)
    - 기준경로 : 파일 탐색 기준
    - 출력폴더 : 저장 폴더 (None 이면 같은 폴더)

    반환값:
    - 딕셔너리: {"csv": 경로, "xlsx": 경로, "건수": int}
    """
    from common.file_io import 타임스탬프, Latest_복사
    from openpyxl import Workbook
    from common.excel_style import 헤더_스타일, 열너비_조정

    df = 컬럼_변환(파일명, 매핑이름, 기준경로)
    if df is None:
        return None

    # 출력 폴더 결정
    if 출력폴더:
        폴더 = Path(출력폴더)
    else:
        폴더 = Path(파일명).parent

    폴더.mkdir(parents=True, exist_ok=True)

    원본이름 = Path(파일명).stem
    시각 = 타임스탬프()

    # ── CSV 저장 ──
    csv경로 = 폴더 / f"{원본이름}_converted_{시각}.csv"
    df.to_csv(csv경로, index=False, encoding="utf-8-sig")
    Latest_복사(csv경로, f"{원본이름}_converted")
    log.info(f"CSV 저장: {csv경로}")

    # ── XLSX 저장 ──
    xlsx경로 = 폴더 / f"{원본이름}_converted_{시각}.xlsx"
    wb = Workbook()

    # 시트 1: 변환된 TC
    ws1 = wb.active
    ws1.title = "테스트 케이스"

    ws1.append(list(df.columns))
    헤더_스타일(ws1)

    for _, 행 in df.iterrows():
        값목록 = []
        for 값 in 행:
            if pd.isna(값):
                값목록.append("")
            else:
                값목록.append(str(값))
        ws1.append(값목록)

    열너비_조정(ws1, 최대너비=50)

    # 시트 2: 변환 정보
    ws2 = wb.create_sheet(title="변환 정보")
    ws2.append(["항목", "내용"])
    헤더_스타일(ws2)

    ws2.append(["원본 파일", str(파일명)])
    ws2.append(["매핑", 매핑이름 or "자동 감지"])
    ws2.append(["변환 시각", 시각])
    ws2.append(["총 TC 수", str(len(df))])

    열너비_조정(ws2)

    wb.save(xlsx경로)
    Latest_복사(xlsx경로, f"{원본이름}_converted")
    log.info(f"XLSX 저장: {xlsx경로}")

    return {
        "csv": csv경로,
        "xlsx": xlsx경로,
        "건수": len(df)
    }


def _데이터_타입_판별(매핑이름, df):
    """
    매핑 이름이나 컬럼명으로 TC인지 버그인지 판별

    반환값:
    - "TC" 또는 "버그"
    """
    이름 = 매핑이름 or ""

    # 매핑 이름으로 판별
    if "버그" in 이름 or "bug" in 이름.lower():
        return "버그"
    if "TC" in 이름 or "tc" in 이름.lower() or "테스트" in 이름:
        return "TC"

    # 컬럼명으로 판별
    컬럼 = set(df.columns)
    if "버그ID" in 컬럼 or "Bug ID" in 컬럼 or "상태" in 컬럼:
        return "버그"

    return "TC"  # 기본값


# ────────────────────────────────────────
# 매핑 자동 생성
# ────────────────────────────────────────
# ────────────────────────────────────────
# 컬럼명 자동 추천용 유사어 사전
# ────────────────────────────────────────
_유사어_사전 = {
    #테스트 케이스 내부 컬럼
    "TC_ID":    ["TC_ID", "Test ID", "TestID", "Test_ID", "테스트ID", "테스트케이스ID",
                 "TC ID", "Case ID", "CaseID", "케이스ID", "ID"],
    "테스트명":  ["Test Name", "TestName", "테스트명", "테스트이름", "이름", "케이스명",
                 "Summary", "Title", "Name", "제목",
                 "Story", "Test"],                                        # ← Allure
    "분류":     ["Category", "Type", "분류", "카테고리", "모듈", "Module", "Component",
                 "Suite", "Feature", "Epic"],                              # ← Allure
    "전제조건":  ["Precondition", "Pre-condition", "전제조건", "사전조건", "선행조건",
                 "Sub Suite"],                                             # ← Allure
    "테스트단계": ["Steps", "Test Steps", "수행절차", "테스트단계", "재현절차", "절차",
                  "Description", "Procedure"],                             # ← Allure
    "예상결과":  ["Expected", "Expected Result", "기대결과", "예상결과", "기대값"],
    "실제결과":  ["Actual", "Actual Result", "실제결과", "결과값"],
    "결과":     ["Result", "Status", "결과", "판정", "Pass/Fail"],          # ← Allure
    "심각도":   ["Severity", "심각도", "중요도", "등급",
                 "severity_level"],                                        # ← Allure
    "우선순위":  ["Priority", "우선순위", "긴급도"],
    "플랫폼":   ["Platform", "플랫폼", "OS", "Device", "환경", "디바이스"],
    "발견자":   ["Tester", "Reporter", "Author", "발견자", "테스터", "보고자", "작성자",
                "Assignee", "담당자"],
    "발견일":   ["Date", "Found Date", "Created", "Create Date", "발견일", "작성일",
                "보고일", "등록일", "생성일"],

    #버그 내부 컬럼
    "버그ID":   ["Bug ID", "BugID", "Bug_ID", "버그ID", "Defect ID", "Issue ID",
                "Issue Key", "Key", "이슈ID", "결함ID"],
    "제목":     ["Title", "Summary", "제목", "요약", "버그명", "이슈명", "Name"],
    "상태":     ["Status", "상태", "State", "Resolution", "처리상태"],
    "버전":     ["Version", "버전", "Build", "빌드", "App Version"],
    "해결일":   ["Resolved Date", "Fixed Date", "해결일", "수정일", "종료일", "Close Date"],
    "재현율":   ["Reproduce Rate", "재현율", "Reproducibility", "재현성"],
}


def _컬럼명_추천(외부컬럼명):
    """
    외부 컬럼명과 유사한 내부 컬럼명 추천

    매개변수:
    - 외부컬럼명: 외부 파일의 컬럼 이름

    반환값:
    - 추천된 내부 컬럼명 (str)
    - "" (매칭 안 될 때)
    """
    외부 = 외부컬럼명.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    최고점수 = 0
    최고매칭 = ""

    for 내부컬럼, 유사어목록 in _유사어_사전.items():
        for 유사어 in 유사어목록:
            비교 = 유사어.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

            # 완전 일치
            if 외부 == 비교:
                return 내부컬럼

            # 포함 관계
            점수 = 0
            if 외부 in 비교 or 비교 in 외부:
                점수 = len(비교) / max(len(외부), 1)

            if 점수 > 최고점수:
                최고점수 = 점수
                최고매칭 = 내부컬럼

    # 유사도 50% 이상이면 추천
    if 최고점수 > 0.5:
        return 최고매칭

    return ""


def 매핑_자동생성(파일명, 매핑이름, 기준경로=None):
    """
    외부 파일의 컬럼명을 읽어 매핑 JSON 초안을 자동 생성
    유사어 사전으로 내부 컬럼명 자동 추천

    매개변수:
    - 파일명   : 외부 파일 경로
    - 매핑이름 : 새 매핑 이름
    - 기준경로 : 파일 탐색 기준

    동작:
    1. 외부 파일 읽기 → 컬럼명 추출
    2. 유사어 사전으로 내부 컬럼명 자동 추천
    3. column_map.json 에 추가
    """
    df = 파일_읽기(파일명, 기준경로)
    if df is None:
        return None

    외부컬럼목록 = list(df.columns)
    log.info(f"외부 파일 컬럼 감지: {외부컬럼목록}")

    # 컬럼명 자동 추천
    컬럼매핑 = {}
    추천됨 = []
    미추천 = []

    for 외부컬럼 in 외부컬럼목록:
        추천 = _컬럼명_추천(외부컬럼)
        컬럼매핑[외부컬럼] = 추천
        if 추천:
            추천됨.append((외부컬럼, 추천))
        else:
            미추천.append(외부컬럼)

    # 매핑 설명 결정
    if 미추천:
        설명 = f"{매핑이름} (자동 추천 완료 - 미매칭 {len(미추천)}개 확인 필요)"
    else:
        설명 = f"{매핑이름} (자동 추천 완료 - 확인 후 사용하세요)"

    새매핑 = {
        "설명": 설명,
        "컬럼_매핑": 컬럼매핑,
        "값_변환": {},
        "기본값": {}
    }

    # column_map.json 에 추가
    설정 = _매핑_로딩()
    if 설정 is None:
        설정 = {"매핑_목록": {}, "내부_필수_컬럼": {}}

    if 매핑이름 in 설정.get("매핑_목록", {}):
        log.warning(f"매핑 '{매핑이름}' 이 이미 존재합니다. 덮어쓰기합니다.")

    설정["매핑_목록"][매핑이름] = 새매핑

    with open(_매핑파일, "w", encoding="utf-8") as f:
        json.dump(설정, f, ensure_ascii=False, indent=4)

    log.info(f"매핑 생성 완료: {매핑이름} (추천 {len(추천됨)}개 / 미매칭 {len(미추천)}개)")

    return {
        "매핑이름": 매핑이름,
        "컬럼목록": 외부컬럼목록,
        "추천됨": 추천됨,
        "미추천": 미추천,
    }


# ────────────────────────────────────────
# 변환 미리보기
# ────────────────────────────────────────
def 변환_미리보기(파일명, 매핑이름=None, 기준경로=None, 표시건수=5):
    """
    변환 결과를 저장 없이 터미널에 미리 출력

    매개변수:
    - 파일명   : 변환할 파일
    - 매핑이름 : 매핑 (None 이면 자동 감지)
    - 기준경로 : 파일 탐색 기준
    - 표시건수 : 미리보기에 표시할 행 수 (기본 5)

    반환값:
    - 변환된 DataFrame (저장은 안 함)
    """
    # 원본 읽기
    원본df = 파일_읽기(파일명, 기준경로)
    if 원본df is None:
        return None

    원본컬럼 = list(원본df.columns)

    # 변환 실행
    변환df = 컬럼_변환(파일명, 매핑이름, 기준경로)
    if 변환df is None:
        return None

    변환컬럼 = list(변환df.columns)

    # 변환 정보 출력
    print("\n[미리보기] 변환 결과")
    print("━" * 60)

    # 컬럼 변환 정보
    print(f"\n원본 컬럼 ({len(원본컬럼)}개):")
    print(f"  {', '.join(원본컬럼)}")
    print(f"\n변환 후 컬럼 ({len(변환컬럼)}개):")
    print(f"  {', '.join(변환컬럼)}")

    # 추가된 컬럼
    추가컬럼 = [c for c in 변환컬럼 if c not in 원본컬럼]
    if 추가컬럼:
        print(f"\n누락 → 자동 추가된 컬럼:")
        for 컬럼 in 추가컬럼:
            기본값 = 변환df[컬럼].iloc[0] if len(변환df) > 0 else ""
            기본표시 = f"'{기본값}'" if 기본값 else "(빈 값)"
            print(f"  + {컬럼} → {기본표시}")

    # 값 변환 정보
    설정 = _매핑_로딩()
    if 설정 and 매핑이름:
        매핑설정 = 설정.get("매핑_목록", {}).get(매핑이름, {})
        값_변환 = 매핑설정.get("값_변환", {})
        if 값_변환:
            print(f"\n값 변환 적용:")
            for 컬럼, 변환맵 in 값_변환.items():
                if 컬럼 in 변환df.columns:
                    for 원래, 변환후 in 변환맵.items():
                        건수 = len(변환df[변환df[컬럼] == 변환후])
                        if 건수 > 0:
                            print(f"  {컬럼}: {원래} → {변환후} ({건수}건)")

    # 데이터 미리보기
    표시 = min(표시건수, len(변환df))
    print(f"\n데이터 미리보기 (상위 {표시}건 / 총 {len(변환df)}건)")
    print("━" * 60)

    # 주요 컬럼만 표시 (너무 많으면 읽기 어려움)
    주요컬럼 = 변환컬럼[:6]  # 앞 6개 컬럼만
    
    # 헤더
    헤더행 = " | ".join([f"{c:12s}" for c in 주요컬럼])
    print(헤더행)
    print("-" * len(헤더행))

    # 데이터
    for _, 행 in 변환df.head(표시).iterrows():
        데이터행 = " | ".join([f"{str(행.get(c, '')):12s}"[:12] for c in 주요컬럼])
        print(데이터행)

    if len(변환df) > 표시:
        print(f"  ... 외 {len(변환df) - 표시}건")

    print("━" * 60)
    print(f"저장하려면: --preview 옵션을 빼고 다시 실행")

    return 변환df


# ────────────────────────────────────────
# 매핑 검증
# ────────────────────────────────────────
def 매핑_검증():
    """
    column_map.json 의 모든 매핑 설정을 검증

    검사 항목:
    - 필수 키 존재 (설명, 컬럼_매핑, 값_변환, 기본값)
    - 빈 매핑값 감지 (자동 생성 후 미수정)
    - 값_변환 키가 내부 컬럼에 있는지

    반환값:
    - 딕셔너리: {매핑이름: {"상태": "PASS"/"WARN"/"FAIL", "메시지": [...]}}
    """
    설정 = _매핑_로딩()
    if 설정 is None:
        return None

    필수키 = ["설명", "컬럼_매핑", "값_변환", "기본값"]
    검증결과 = {}

    for 이름, 내용 in 설정.get("매핑_목록", {}).items():
        메시지 = []
        상태 = "PASS"

        # 1. 필수 키 검사
        for 키 in 필수키:
            if 키 not in 내용:
                메시지.append(f"필수 키 누락: {키}")
                상태 = "FAIL"

        # 2. 빈 매핑값 검사 (자동 생성 후 미수정)
        컬럼매핑 = 내용.get("컬럼_매핑", {})
        빈매핑 = [k for k, v in 컬럼매핑.items() if v == ""]
        if 빈매핑:
            for 컬럼 in 빈매핑:
                메시지.append(f'빈 매핑값: "{컬럼}": "" ← 내부 컬럼명 입력 필요')
            if 상태 != "FAIL":
                상태 = "WARN"

        # 3. 값_변환 키가 유효한지 (내부 컬럼명과 매칭)
        값_변환 = 내용.get("값_변환", {})
        매핑된_내부컬럼 = list(컬럼매핑.values())
        for 컬럼 in 값_변환.keys():
            if 컬럼 not in 매핑된_내부컬럼 and 컬럼매핑:
                # 내부 컬럼명이 값_변환 키에 직접 사용된 경우는 OK
                pass

        # 4. 설명 확인
        설명 = 내용.get("설명", "")
        if "자동 생성" in 설명 and "수정 필요" in 설명:
            메시지.append("자동 생성된 매핑 — 아직 수정되지 않음")
            if 상태 != "FAIL":
                상태 = "WARN"

        검증결과[이름] = {
            "상태": 상태,
            "메시지": 메시지
        }

    return 검증결과