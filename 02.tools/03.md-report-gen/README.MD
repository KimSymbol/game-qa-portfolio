# 📄 MD Report Generator

테스트 케이스 파일(CSV/XLSX)을 읽어
Fail 케이스를 마크다운 버그 리포트로 자동 생성하는 도구입니다.

---

## 📁 프로젝트 구조

```
04.md-report-gen/
├── md_generator.py    # 핵심 모듈
├── main.py            # 실행 파일
├── README.md
└── 결과/
    ├── bug_reports/
    │   ├── BUG-001.md
    │   ├── BUG-002.md
    │   └── BUG-003.md
    ├── ALL_BUGS.md
    └── bugs_YYYY-MM-DD.csv
```

---

## ⚙️ 설치

```bash
pip install pandas openpyxl
```

---

## 🚀 실행 방법

```bash
# 기본 파일 (testcases.csv) 분석
python main.py

# CSV 파일 지정
python main.py testcases.csv

# XLSX 파일 지정
python main.py testcases.xlsx

# 여러 파일
python main.py a.csv b.xlsx

# 폴더 지정 → 안의 csv/xlsx 전부 분석
python main.py data/
```

> 상위 폴더에서 실행할 때
> ```bash
> python 04.md-report-gen/main.py
> python 04.md-report-gen/main.py testcases.xlsx
> ```

---

## 📄 입력 파일 형식

### 지원 형식

| 형식 | 확장자 | 인코딩 |
|------|--------|--------|
| CSV | `.csv` | UTF-8 / UTF-8-BOM |
| 엑셀 | `.xlsx` | - |

### 필수 컬럼

| 컬럼명 | 형식 | 예시 | 필수 여부 |
|--------|------|------|----------|
| TC_ID | TC-001 | TC-001 | ✅ 필수 |
| 테스트명 | 문자열 | 로그인 확인 | ✅ 필수 |
| 결과 | Pass/Fail/Block/Skip | Fail | ✅ 필수 |
| 심각도 | Critical/High/Medium/Low | Critical | ✅ 필수 |
| 우선순위 | High/Medium/Low | High | ✅ 필수 |
| 플랫폼 | PC/Android/iOS 등 | PC | ✅ 필수 |
| 발견자 | 문자열 | 홍길동 | ✅ 필수 |
| 발견일 | YYYY-MM-DD | 2026-06-17 | ✅ 필수 |
| 테스트단계 | 문자열 | 1. 앱 실행\n2. 클릭 | ⬜ 선택 |
| 예상결과 | 문자열 | 정상 동작 | ⬜ 선택 |
| 실제결과 | 문자열 | 오류 발생 | ⬜ 선택 |
| 분류 | 문자열 | 로그인 | ⬜ 선택 |
| 버전 | 문자열 | v1.2.34 | ⬜ 선택 |
| 재현율 | N/10 | 8/10 | ⬜ 선택 |

> `test-data-gen` 의 `testcases_YYYY-MM-DD.csv` 형식과 동일하여 바로 사용 가능

### 규칙

- `결과` 컬럼이 `Fail` 인 행만 버그 리포트로 생성됩니다
- 버그 ID는 `BUG-001` 부터 자동 순번 생성됩니다
- TC_ID는 버그 리포트에 참조 항목으로 기록됩니다

---

## 📊 출력 파일 구성

| 파일 | 내용 |
|------|------|
| `bug_reports/BUG-001.md` | 개별 버그 마크다운 리포트 |
| `ALL_BUGS.md` | 전체 버그 통합 마크다운 리포트 |
| `bugs_YYYY-MM-DD.csv` | excel-reporter 입력용 CSV |

---

## 🔗 도구 연동

```bash
# 1. test-data-gen 으로 테스트 케이스 생성
python 03.test-data-gen/main.py testcases

# 2. md-report-gen 으로 마크다운 리포트 생성
python 04.md-report-gen/main.py 03.test-data-gen/결과/testcases_2026-06-17.csv

# 3. 생성된 bugs.csv 로 엑셀 리포트 생성
python 02.excel-reporter/main.py 04.md-report-gen/결과/bugs_2026-06-17.csv
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `pandas` | CSV/XLSX 읽기 |
| `openpyxl` | XLSX 파일 읽기 |
| `csv` | bugs.csv 저장 |
| `pathlib` | 경로 관리 / 폴더 자동 생성 |
| `datetime` | 날짜별 파일명 자동 생성 |