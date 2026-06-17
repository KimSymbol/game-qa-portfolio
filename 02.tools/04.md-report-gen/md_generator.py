# 역할: 테스트 케이스 파일을 읽어 마크다운 버그 리포트를 자동 생성하는 모듈
# 지원 형식: .csv / .xlsx
# 다른 모듈(main.py)에서 import해서 사용
#
# 입력 → 출력:
#   testcases.csv / .xlsx → BUG-001.md, ALL_BUGS.md, bugs.csv

import csv
import pandas as pd
from pathlib import Path
from datetime import datetime

# md_generator.py 가 있는 폴더를 기준 경로로 설정
기준경로 = Path(__file__).parent

# 심각도 기준 설명 (마크다운 리포트 하단에 삽입)
심각도기준 = """
## 심각도 기준

| 심각도 | 기준 |
|--------|------|
| **Critical** | 게임 진행 불가, 크래시, 데이터 손실 |
| **High** | 주요 기능 오작동, 반복 재현 가능 |
| **Medium** | 일부 기능 이상, 우회 방법 있음 |
| **Low** | UI 오탈자, 시각적 결함, 경미한 이상 |
"""


# ────────────────────────────────────────
# ① 파일 읽기 (.csv / .xlsx 자동 판단)
# ────────────────────────────────────────
def 파일_읽기(파일명):
    """
    CSV 또는 XLSX 파일을 읽어서 DataFrame으로 반환

    매개변수:
    - 파일명: 읽을 파일 이름 (예: "testcases.csv" / "testcases.xlsx")
              기준경로(md_generator.py 위치) 기준으로 찾음

    반환값:
    - DataFrame: 테스트 케이스 데이터
    - None: 파일이 없거나 지원하지 않는 형식일 때

    지원 형식:
    - .csv  : UTF-8 / UTF-8-BOM 인코딩
    - .xlsx : 엑셀 파일
    """
    경로 = 기준경로 / 파일명

    # 절대 경로로 시도 (다른 폴더 파일 지정 시)
    if not 경로.exists():
        # md_generator.py 위치 기준
        경로 = 기준경로 / 파일명

    if not 경로.exists():
        print("❌ 파일이 없어요:", 경로)
        return None

    확장자 = 경로.suffix.lower()

    if 확장자 == ".csv":
        # utf-8-sig → BOM 있는 파일도 없는 파일도 둘 다 정상 읽힘
        df = pd.read_csv(경로, encoding="utf-8-sig")
    elif 확장자 == ".xlsx":
        df = pd.read_excel(경로)
    else:
        print(f"❌ 지원하지 않는 형식이에요: {확장자} (csv / xlsx 만 가능)")
        return None

    print(f"✅ 파일 로딩 완료: {len(df)}건 ({확장자})")
    return df


# ────────────────────────────────────────
# ② Fail 케이스만 추출
# ────────────────────────────────────────
def Fail_추출(df):
    """
    전체 테스트 케이스에서 결과가 Fail 인 것만 추출

    매개변수:
    - df: 파일_읽기()로 읽은 전체 테스트 케이스 DataFrame

    반환값:
    - DataFrame: 결과가 Fail 인 행만 포함
    - None: Fail 케이스 없을 때

    동작:
    - "결과" 컬럼에서 "Fail" 인 행만 필터링
    - 인덱스 리셋 (0번부터 다시 시작)
    """
    fail_df = df[df["결과"] == "Fail"].reset_index(drop=True)

    if len(fail_df) == 0:
        print("✅ Fail 케이스가 없어요!")
        return None

    print(f"🔴 Fail 케이스: {len(fail_df)}건")
    return fail_df


# ────────────────────────────────────────
# ③ 재현 절차 포맷팅
# ────────────────────────────────────────
def 재현절차_포맷(테스트단계):
    """
    테스트 단계 문자열을 마크다운 번호 목록으로 변환

    매개변수:
    - 테스트단계: 테스트 단계 문자열
                  줄바꿈(\n) 또는 숫자(1. 2. 3.) 형식

    반환값:
    - 마크다운 번호 목록 문자열

    예시:
    입력: "앱 실행\n버튼 클릭\n결과 확인"
    출력: "1. 앱 실행\n2. 버튼 클릭\n3. 결과 확인"
    """
    if pd.isna(테스트단계) or str(테스트단계).strip() == "":
        return "1. \n2. \n3. "

    # 줄바꿈으로 분리
    단계들 = str(테스트단계).strip().split("\n")

    # 각 줄 앞의 기존 번호 제거 후 재번호 부여
    결과 = []
    번호 = 1
    for 단계 in 단계들:
        # "1. " "2. " 형식 제거
        단계 = 단계.strip().lstrip("0123456789. ")
        if 단계:
            결과.append(f"{번호}. {단계}")
            번호 += 1

    return "\n".join(결과) if 결과 else "1. \n2. \n3. "


# ────────────────────────────────────────
# ④ 마크다운 리포트 단일 생성
# ────────────────────────────────────────
def 마크다운_생성(버그ID, TC_ID, 행):
    """
    버그 하나의 마크다운 리포트 문자열 생성

    매개변수:
    - 버그ID : 생성된 버그 ID (예: "BUG-001")
    - TC_ID  : 참조 테스트 케이스 ID (예: "TC-002")
    - 행     : DataFrame 의 한 행 (Series)

    반환값:
    - 마크다운 문자열

    템플릿:
    - 버그 요약 테이블 (심각도, 우선순위, TC ID 등)
    - 재현 절차
    - 예상/실제 결과
    - 첨부 자료
    - 참고 사항
    - 심각도 기준표
    """
    # 값 안전하게 꺼내기 (없으면 빈 값)
    def 값(컬럼, 기본=""):
        try:
            v = 행.get(컬럼, 기본)
            return "" if pd.isna(v) else str(v).strip()
        except:
            return 기본

    제목      = 값("테스트명", "버그 제목")
    심각도    = 값("심각도",   "")
    우선순위  = 값("우선순위", "")
    발견자    = 값("발견자",   "")
    발견일    = 값("발견일",   datetime.now().strftime("%Y-%m-%d"))
    플랫폼    = 값("플랫폼",   "")
    버전      = 값("버전",     "")
    재현율    = 값("재현율",   "")
    테스트단계 = 값("테스트단계", "")
    예상결과  = 값("예상결과", "")
    실제결과  = 값("실제결과", "")
    분류      = 값("분류",     "")

    재현절차 = 재현절차_포맷(테스트단계)

    마크다운 = f"""## [{버그ID}] {제목}

| 항목 | 내용 |
|------|------|
| **심각도 (Severity)** | {심각도} |
| **우선순위 (Priority)** | {우선순위} |
| **테스트 케이스** | {TC_ID} |
| **분류** | {분류} |
| **발견 날짜** | {발견일} |
| **발견자** | {발견자} |
| **플랫폼** | {플랫폼} |
| **버전** | {버전} |
| **재현율** | {재현율} |

---

### 요약 (Summary)
> {제목}

### 재현 절차 (Steps to Reproduce)
{재현절차}

### 예상 결과 (Expected Result)
> {예상결과}

### 실제 결과 (Actual Result)
> {실제결과}

### 첨부 자료 (Attachments)
- 스크린샷:
- 동영상:
- 로그:

### 참고 사항 (Notes)
> 추가로 알아야 할 맥락, 연관 버그 등

---
{심각도기준}"""

    return 마크다운


# ────────────────────────────────────────
# ⑤ 개별 .md 파일 저장
# ────────────────────────────────────────
def 개별_저장(버그ID, 마크다운내용):
    """
    버그 하나의 마크다운을 개별 파일로 저장

    매개변수:
    - 버그ID       : 파일명에 사용할 버그 ID (예: "BUG-001")
    - 마크다운내용 : 저장할 마크다운 문자열

    저장 위치: 결과/bug_reports/BUG-001.md
    """
    저장폴더 = 기준경로 / "결과" / "bug_reports"
    저장폴더.mkdir(parents=True, exist_ok=True)

    파일명 = 저장폴더 / f"{버그ID}.md"
    with open(파일명, "w", encoding="utf-8") as f:
        f.write(마크다운내용)

    return 파일명


# ────────────────────────────────────────
# ⑥ 전체 통합 .md 파일 저장
# ────────────────────────────────────────
def 통합_저장(마크다운목록):
    """
    모든 버그 리포트를 하나의 파일로 통합 저장

    매개변수:
    - 마크다운목록: 개별 마크다운 문자열 리스트

    저장 위치: 결과/ALL_BUGS.md
    """
    결과폴더 = 기준경로 / "결과"
    결과폴더.mkdir(exist_ok=True)

    파일명 = 결과폴더 / "ALL_BUGS.md"

    오늘 = datetime.now().strftime("%Y-%m-%d")
    헤더 = f"# 🐛 전체 버그 리포트\n\n생성일: {오늘} | 총 {len(마크다운목록)}건\n\n---\n\n"

    with open(파일명, "w", encoding="utf-8") as f:
        f.write(헤더)
        f.write("\n\n---\n\n".join(마크다운목록))

    return 파일명


# ────────────────────────────────────────
# ⑦ bugs.csv 저장 (excel-reporter 연동용)
# ────────────────────────────────────────
def bugs_csv_저장(fail_df, 버그ID목록):
    """
    Fail 케이스를 excel-reporter 입력 형식의 CSV로 저장

    매개변수:
    - fail_df   : Fail 케이스만 담긴 DataFrame
    - 버그ID목록: 생성된 버그 ID 리스트

    저장 위치: 결과/bugs_YYYY-MM-DD.csv

    컬럼 매핑 (testcases → bugs.csv):
    - 새 버그ID        → 버그ID
    - 테스트명         → 제목
    - 심각도           → 심각도
    - 우선순위         → 우선순위
    - 플랫폼           → 플랫폼
    - 버전             → 버전
    - 발견자           → 발견자
    - 발견일           → 발견일
    - "미해결" 고정    → 상태
    - TC_ID 참조       → TC_ID (추가 컬럼)
    """
    결과폴더 = 기준경로 / "결과"
    결과폴더.mkdir(exist_ok=True)

    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 결과폴더 / f"bugs_{오늘}.csv"

    def 값_안전(행, 컬럼, 기본=""):
        try:
            v = 행.get(컬럼, 기본)
            return "" if pd.isna(v) else str(v).strip()
        except:
            return 기본

    헤더 = ["버그ID", "TC_ID", "제목", "심각도", "우선순위",
            "플랫폼", "버전", "상태", "발견자", "발견일", "해결일", "재현율"]

    with open(파일명, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(헤더)

        for i, (_, 행) in enumerate(fail_df.iterrows()):
            writer.writerow([
                버그ID목록[i],
                값_안전(행, "TC_ID"),
                값_안전(행, "테스트명"),
                값_안전(행, "심각도"),
                값_안전(행, "우선순위"),
                값_안전(행, "플랫폼"),
                값_안전(행, "버전"),
                "미해결",              # 상태 기본값
                값_안전(행, "발견자"),
                값_안전(행, "발견일"),
                "",                    # 해결일 빈 값
                값_안전(행, "재현율"),
            ])

    return 파일명


# ────────────────────────────────────────
# ⑧ 전체 리포트 생성 (메인 함수)
# ────────────────────────────────────────
def 리포트_생성(파일명):
    """
    파일을 읽어서 마크다운 리포트 + bugs.csv 전체 생성

    매개변수:
    - 파일명: 분석할 CSV 또는 XLSX 파일 이름

    동작 순서:
    1. 파일 읽기 (CSV/XLSX 자동 판단)
    2. Fail 케이스 추출
    3. 버그 ID 순번 생성 (BUG-001 부터)
    4. 개별 마크다운 파일 저장
    5. 통합 마크다운 파일 저장
    6. bugs.csv 저장 (excel-reporter 연동용)

    반환값:
    - 딕셔너리: {"개별": [경로목록], "통합": 경로, "csv": 경로}
    """
    # 1. 파일 읽기
    df = 파일_읽기(파일명)
    if df is None:
        return None

    # 2. Fail 케이스 추출
    fail_df = Fail_추출(df)
    if fail_df is None:
        return None

    # 3. 버그 ID 순번 생성 (BUG-001 부터)
    버그ID목록 = [f"BUG-{i+1:03d}" for i in range(len(fail_df))]

    # 4. 개별 마크다운 생성 + 저장
    마크다운목록 = []
    개별경로목록 = []

    for i, (_, 행) in enumerate(fail_df.iterrows()):
        버그ID = 버그ID목록[i]
        TC_ID  = str(행.get("TC_ID", "")).strip()

        마크다운 = 마크다운_생성(버그ID, TC_ID, 행)
        경로     = 개별_저장(버그ID, 마크다운)

        마크다운목록.append(마크다운)
        개별경로목록.append(경로)
        print(f"✅ {버그ID} 생성 완료 (참조: {TC_ID})")

    # 5. 통합 마크다운 저장
    통합경로 = 통합_저장(마크다운목록)

    # 6. bugs.csv 저장 (excel-reporter 연동용)
    csv경로 = bugs_csv_저장(fail_df, 버그ID목록)

    return {
        "개별": 개별경로목록,
        "통합": 통합경로,
        "csv" : csv경로
    }