# 📄 MD Report Generator

테스트 케이스 파일(CSV/XLSX)을 읽어 **Fail 케이스를 마크다운 버그 리포트로 자동 생성**하는 도구입니다.

---

## 📁 프로젝트 구조

```
03.md-report-gen/
├── md_generator.py    # 핵심 모듈
├── main.py            # 실행 파일
├── README.md
└── 결과/              # ⚠️ .gitignore 로 제외됨 (실행 시 자동 생성)
    ├── bug_reports/
    │   ├── BUG-001.md
    │   ├── BUG-002.md
    │   └── ...
    ├── ALL_BUGS_YYYY-MM-DD_HH-MM-SS.md
    ├── ALL_BUGS_latest.md
    ├── bugs_YYYY-MM-DD_HH-MM-SS.csv
    └── bugs_latest.csv
```

> 💡 `결과/` 폴더는 `.gitignore` 에 추가되어 있어 GitHub 에 올라가지 않습니다.

---

## ⚙️ 설치

```bash
pip install pandas openpyxl
```

---

## 🚀 실행 방법

```bash
# CSV 파일 지정
python main.py testcases.csv

# XLSX 파일 지정
python main.py testcases.xlsx

# 여러 파일
python main.py a.csv b.xlsx

# 폴더 안 csv/xlsx 전부 분석
python main.py data/
```

---
## 빈 버그 리포트 템플릿 생성

QA가 수동으로 버그를 작성할 때 사용할 빈 마크다운 템플릿을 생성합니다.

```bash
# 기본 5건
python main.py --template

# 건수 지정
python main.py --template 10
```


### 템플릿 내용

각 .md 파일에는 아래 항목이 비어있는 상태로 포함됩니다.

- 심각도, 우선순위, 테스트 케이스, 분류
- 발견 날짜, 발견자, 플랫폼, 버전, 재현율
- 요약, 재현 절차, 예상 결과, 실제 결과
- 첨부 자료, 참고 사항

---

## 📄 입력 파일 형식

### 필수 컬럼

| 컬럼명 | 형식 | 필수 여부 |
|--------|------|----------|
| TC_ID | TC-001 | ✅ 필수 |
| 테스트명 | 문자열 | ✅ 필수 |
| 결과 | Pass/Fail/Block/Skip | ✅ 필수 |
| 심각도 | Critical/High/Medium/Low | 🔶 Fail 시 |
| 우선순위 | High/Medium/Low | 🔶 Fail 시 |
| 발견자, 발견일, 플랫폼 | - | ✅ 필수 |
| 테스트단계, 예상결과, 실제결과 | 문자열 | ⬜ 선택 |

> 💡 `결과` 컬럼이 `Fail` 인 행만 버그 리포트로 생성됩니다.

---

## 📊 출력 파일 구성

| 파일 | 내용 |
|------|------|
| `bug_reports/BUG-001.md` | 개별 버그 마크다운 (심각도 기준표 포함) |
| `ALL_BUGS_*.md` | 전체 버그 통합 (심각도 기준표 1회) |
| `bugs_*.csv` | excel-reporter 연동용 CSV |

### 마크다운 리포트 예시

```markdown
## [BUG-001] 캐릭터가 벽을 통과함

| 항목 | 내용 |
|------|------|
| **심각도** | Critical |
| **우선순위** | High |
| **테스트 케이스** | TC-002 |
| **발견 날짜** | 2026-06-17 |

### 요약
> 캐릭터가 벽을 통과함

### 재현 절차
1. 앱 실행
2. 캐릭터 이동
3. 벽으로 진입

### 예상 결과
> 벽에 막힘

### 실제 결과
> 벽을 통과함
```

---

## 🔗 도구 연동

```bash
# 1. test-data-gen 으로 테스트 케이스 생성
python 01.test-data-gen/main.py testcases

# 2. md-report-gen 으로 마크다운 리포트 생성
python 03.md-report-gen/main.py 01.test-data-gen/결과/testcases_latest.csv

# 3. 생성된 bugs.csv 로 엑셀 리포트
python 04.excel-reporter/main.py 03.md-report-gen/결과/bugs_latest.csv --all
```

---

## 🔧 유지보수 & 커스터마이즈 가이드

### 1. 마크다운 템플릿 수정

`md_generator.py` 의 `마크다운_생성()` 함수 내부 f-string 만 수정하면 됩니다.

```python
def 마크다운_생성(버그ID, TC_ID, 행, 심각도기준_포함=True):
    마크다운 = f"""## [{버그ID}] {제목}

| 항목 | 내용 |
|------|------|
| **심각도 (Severity)** | {심각도} |
| **우선순위 (Priority)** | {우선순위} |
| **추가 항목** | {새로운필드}      ← 항목 추가
...
"""
```

### 2. 심각도 기준 수정

상단의 `심각도기준` 상수만 수정하면 모든 리포트에 일괄 반영.

```python
심각도기준 = """
## 심각도 기준

| 심각도 | 기준 |
|--------|------|
| **Critical** | ... |
"""
```

### 3. bugs.csv 출력 컬럼 변경

`bugs_csv_저장()` 함수의 `헤더` 리스트만 수정.

```python
헤더 = ["버그ID", "TC_ID", "제목", "심각도", "우선순위",
        "플랫폼", "버전", "상태", "발견자", "발견일", "해결일", "재현율"]
```

### 누락 컬럼 자동 보완

외부 데이터에 필수 컬럼이 없어도 기본값을 자동으로 채워서 동작합니다.

| 누락 컬럼 | 기본값 |
|----------|--------|
| 결과 | (빈 값) |
| 심각도 | (빈 값) |
| 우선순위 | (빈 값) |
| 플랫폼 | PC |
| 발견자~재현율 | (빈 값) |

### "결과" 컬럼이 없을 때

"결과" 컬럼 자체가 없으면 전체 데이터를 대상으로 버그 리포트를 생성합니다.

```bash
# 결과 컬럼 없는 파일 → 전체 행을 버그 리포트로 변환
python main.py external_bugs.csv
# [WARN] '결과' 컬럼 없음 - 전체 데이터를 대상으로 처리
```


---

## 🛠️ 트러블슈팅

### 1. NaN 값이 "nan" 으로 출력돼요

**원인**: pandas 의 NaN 값을 그대로 문자열 변환

**해결**: `값()` 헬퍼 함수에서 `pd.isna()` 체크
```python
def 값(컬럼, 기본=""):
    v = 행.get(컬럼, 기본)
    return "" if pd.isna(v) else str(v).strip()
```

### 2. 재현 절차 번호가 이상해요

**원인**: 입력 데이터에 이미 번호가 있는 경우

**해결**: `재현절차_포맷()` 함수에서 기존 번호 제거 후 재번호
```python
단계 = 단계.strip().lstrip("0123456789. ")
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `pandas` | CSV/XLSX 읽기 |
| `csv` | bugs.csv 저장 |
| `pathlib` | 경로 관리 |
| `common.file_io` | 공통 입출력 모듈 |
| `common.logger` | 로깅 시스템 |