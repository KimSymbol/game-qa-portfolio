# 📊 Excel Reporter

버그 데이터를 **5시트 엑셀 + JSON + HTML + PDF** 4가지 형식으로 동시 변환하는 통합 리포트 도구입니다.

---

## 📁 프로젝트 구조

```
04.excel-reporter/
├── reporter.py        # 핵심 모듈 (5시트 + 4형식 출력)
├── main.py            # 실행 파일
├── README.md
└── 결과/              # ⚠️ .gitignore 로 제외됨 (실행 시 자동 생성)
    ├── report_YYYY-MM-DD_HH-MM-SS.xlsx
    ├── report_YYYY-MM-DD_HH-MM-SS.json
    ├── report_YYYY-MM-DD_HH-MM-SS.html
    ├── report_YYYY-MM-DD_HH-MM-SS.pdf
    └── report_latest.{xlsx,json,html,pdf}
```

> 💡 `결과/` 폴더는 `.gitignore` 에 추가되어 있어 GitHub 에 올라가지 않습니다.

---

## ⚙️ 설치

```bash
pip install pandas openpyxl reportlab
```

> 💡 `reportlab` 은 PDF 생성에 사용됩니다.

---

## 🚀 실행 방법

```bash
# 엑셀만 생성 (기본)
python main.py bugs.csv

# 모든 출력 형식
python main.py bugs.csv --all

# 특정 형식만
python main.py bugs.csv --json
python main.py bugs.csv --html
python main.py bugs.csv --pdf
python main.py bugs.csv --excel

# 폴더 안 csv/xlsx/tsv/json 전부
python main.py data/ --all
```

---

## 📊 5시트 엑셀 리포트 구성

| 시트 | 내용 |
|------|------|
| 전체 버그 목록 | 모든 버그 (심각도별 색상 구분) |
| 발견자별 현황 | 발견자 × 상태 교차표 |
| 플랫폼별 현황 | 플랫폼 × 심각도 교차표 |
| 심각도·우선순위 | 통계 요약 |
| 요약 대시보드 | 총 버그/해결률/상태/심각도/우선순위/플랫폼 종합 |

---

## 📄 출력 형식 비교

| 형식 | 용도 | 특징 |
|------|------|------|
| **xlsx** | 실무 분석 | 5시트 색상 구분 |
| **json** | API 연동, 자동화 | 통계 + 상세 데이터 |
| **html** | 웹 / 메일 | 브라우저 바로 보기 |
| **pdf** | 공식 보고서 | 한글 폰트 자동 적용 |

---

## 📄 입력 파일 형식

### 지원 형식

| 형식 | 확장자 |
|------|--------|
| CSV | `.csv` |
| TSV | `.tsv` |
| Excel | `.xlsx` |
| JSON | `.json` (리스트 형태) |

### 필수 컬럼

| 컬럼명 | 예시 |
|--------|------|
| 버그ID | BUG-001 |
| 제목 | 캐릭터가 벽을 통과함 |
| 심각도 | Critical / High / Medium / Low |
| 우선순위 | High / Medium / Low |
| 플랫폼 | PC / Android / iOS |
| 상태 | 해결 / 진행중 / 미해결 |
| 발견자, 발견일 | - |

---

## 🔗 도구 연동

```bash
# 옵션 1: test-data-gen → excel-reporter
python 01.test-data-gen/main.py bugs
python 04.excel-reporter/main.py 01.test-data-gen/결과/bugs_latest.csv --all

# 옵션 2: md-report-gen → excel-reporter (Fail TC → 버그 리포트화)
python 03.md-report-gen/main.py 01.test-data-gen/결과/testcases_latest.csv
python 04.excel-reporter/main.py 03.md-report-gen/결과/bugs_latest.csv --all
```

---

## 🔧 유지보수 & 커스터마이즈 가이드

### 1. 시트 추가하기

#### Step 1. `reporter.py` 에 시트 함수 추가

```python
def 시트_월별통계(wb, df):
    """월별 발견 추이 시트 (예시)"""
    ws = wb.create_sheet(title="월별 통계")
    ws.append(["월", "버그 수"])
    헤더_스타일(ws)

    df["월"] = pd.to_datetime(df["발견일"]).dt.month
    월별 = df.groupby("월").size()

    for 월, 수 in 월별.items():
        ws.append([f"{월}월", 수])
        # ... 스타일 ...

    열너비_조정(ws)
```

#### Step 2. `리포트_생성()` 에 호출 추가

```python
def 리포트_생성(df):
    wb = Workbook()
    시트_전체목록(wb, df)
    시트_발견자별(wb, df)
    시트_월별통계(wb, df)    # ← 추가
    ...
```

### 2. HTML 스타일 변경

`common/file_io.py` 의 `HTML_쓰기()` 함수 내부 CSS 수정.

### 3. PDF 한글 폰트 변경

`common/file_io.py` 의 `PDF_쓰기()` 함수에서 폰트 경로 변경.

```python
한글폰트경로목록 = [
    "C:/Windows/Fonts/NanumGothic.ttf",  # ← 나눔고딕으로 변경
    ...
]
```

---

## 🛠️ 트러블슈팅

### 1. PDF 한글이 □ 로 표시돼요

**원인**: 한글 폰트 등록 실패

**해결**: 시스템에 맑은 고딕(`malgun.ttf`) 또는 나눔고딕 설치 확인

### 2. 차트가 안 보여요

**원인**: openpyxl 차트의 데이터 레이블 표시 제약

**해결**: 차트 대신 **색상 구분 테이블** 사용 (현재 적용됨)

### 3. 병합 셀 에러

**증상**: `AttributeError: 'MergedCell' object`

**해결**: `get_column_letter()` 로 열 이름 가져오기
```python
from openpyxl.utils import get_column_letter
열이름 = get_column_letter(i)
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `pandas` | 데이터 분석 |
| `openpyxl` | 엑셀 생성 |
| `reportlab` | PDF 생성 (한글 폰트 자동) |
| `common.file_io` | 공통 입출력 (xlsx/json/html/pdf) |
| `common.excel_style` | 엑셀 공통 스타일 |
| `common.logger` | 로깅 시스템 |