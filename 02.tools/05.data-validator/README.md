# 📋 Data Validator

CSV 파일의 데이터 무결성을 자동으로 검사하는 도구입니다.
검사 규칙은 JSON 파일로 관리하며, 규칙 파일 없이도 기본 검사가 가능합니다.

---

## 📁 프로젝트 구조

```
05.data-validator/
├── validator.py      # 핵심 모듈
├── main.py           # 실행 파일
├── README.md
├── rules/            # 검사 규칙 설정 파일
│   ├── bugs.json     # bugs.csv 검사 규칙
│   ├── testcases.json# testcases.csv 검사 규칙
│   └── default.json  # 기본 규칙
└── 결과/
    └── validation_report_YYYY-MM-DD.xlsx
```

---

## ⚙️ 설치

```bash
pip install pandas openpyxl
```

---

## 🚀 실행 방법

```bash
# 파일 지정
python main.py bugs.csv

# 여러 파일
python main.py bugs.csv testcases.csv

# 폴더 지정 → 안의 csv 전부 검사
python main.py data/
```

> ⚠️ 파일을 반드시 지정해야 합니다.
>
> **test-data-gen 과 연동 시**
> ```bash
> python 03.test-data-gen/main.py bugs
> python 05.data-validator/main.py 03.test-data-gen/결과/bugs_2026-06-17.csv
> ```

---

## 📋 검사 항목

| 검사 | 설명 | 규칙 파일 필요? |
|------|------|---------------|
| 필수컬럼 | 필수 컬럼 존재 여부 | ✅ 필요 |
| 빈값 | 필수 항목 누락 | 🔶 없으면 전체 검사 |
| 허용값 | 오타/잘못된 값 (예: "Critcal") | ✅ 필요 |
| 날짜형식 | 날짜 형식 오류 | ✅ 필요 |
| 중복 | 중복 데이터 | 🔶 없으면 전체 행 검사 |
| 패턴 | 정규표현식 패턴 불일치 | ✅ 필요 |
| 공백 | 앞뒤 공백 오류 | ❌ 항상 검사 |

---

## 📄 규칙 파일 형식 (JSON)

### 규칙 파일 자동 매핑

| 파일 이름에 포함 | 사용되는 규칙 |
|-----------------|-------------|
| "bugs" | `rules/bugs.json` |
| "testcases" | `rules/testcases.json` |
| 그 외 | `rules/default.json` |
| 전부 없음 | 내장 기본 규칙 (빈값, 중복, 공백만) |

### 규칙 파일 예시 (bugs.json)

```json
{
    "설명": "bugs.csv 검사 규칙",
    "필수_컬럼": ["버그ID", "제목", "심각도", "상태"],
    "컬럼_규칙": {
        "버그ID": {
            "필수": true,
            "중복불가": true,
            "패턴": "BUG-\\d+"
        },
        "심각도": {
            "필수": true,
            "허용값": ["Critical", "High", "Medium", "Low"]
        },
        "발견일": {
            "필수": true,
            "날짜형식": "%Y-%m-%d"
        }
    }
}
```

### 컬럼 규칙 속성

| 속성 | 값 | 설명 |
|------|------|------|
| `필수` | true/false | 빈 값 허용 여부 |
| `중복불가` | true/false | 중복 값 허용 여부 |
| `허용값` | ["A", "B"] | 허용되는 값 목록 |
| `날짜형식` | "%Y-%m-%d" | 날짜 형식 |
| `패턴` | "BUG-\\\\d+" | 정규표현식 패턴 |

---

## 📊 검증 리포트

| 시트 | 내용 |
|------|------|
| 오류 목록 | 전체 오류 상세 내역 (유형별 색상 구분) |
| 요약 | 검사 유형별 통과/실패 현황 |

---

## 🔗 도구 연동

```bash
# 1. test-data-gen 으로 데이터 생성
python 03.test-data-gen/main.py bugs

# 2. data-validator 로 데이터 검증
python 05.data-validator/main.py 03.test-data-gen/결과/bugs_2026-06-17.csv

# 3. 검증 통과 후 excel-reporter 로 리포트 생성
python 02.excel-reporter/main.py 03.test-data-gen/결과/bugs_2026-06-17.csv
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `pandas` | CSV 읽기 및 데이터 분석 |
| `openpyxl` | 검증 리포트 엑셀 생성 |
| `re` | 정규표현식 패턴 검사 |
| `json` | 규칙 파일 읽기 |
| `pathlib` | 경로 관리 |
| `datetime` | 날짜 형식 검사 |