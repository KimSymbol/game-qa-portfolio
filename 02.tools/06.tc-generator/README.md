# 테스트 케이스 자동 생성기

JSON 사양 파일을 기반으로 테스트 케이스를 자동 생성하는 도구입니다.
동등분할, 경계값 분석, 결정 테이블 기법으로 다양한 시나리오를 자동 생성합니다.

---

## 프로젝트 구조

```
06.tc-generator/
├── tc_generator.py    # 핵심 모듈
├── main.py            # 실행 파일
├── README.md
├── specs/             # 기능 사양 JSON
│   ├── login.json
│   ├── inventory.json
│   ├── shop.json
│   └── battle.json
└── 결과/              # .gitignore 로 제외됨 (실행 시 자동 생성)
    ├── testcases_로그인_YYYY-MM-DD_HH-MM-SS.csv
    ├── testcases_로그인_YYYY-MM-DD_HH-MM-SS.xlsx
    ├── testcases_로그인_latest.csv
    └── testcases_로그인_latest.xlsx
```

---

## 설치

```bash
pip install pandas openpyxl
```

---

## 실행 방법

```bash
# specs/ 폴더 전체 사양으로 TC 생성
python main.py

# 특정 사양만
python main.py login.json

# 여러 사양
python main.py login.json shop.json

# 빈 템플릿 생성 (직접 수기 작성용)
python main.py --template
```

---

## JSON 사양 파일 형식

### login.json 예시

```json
{
    "기능명": "로그인",
    "분류": "로그인",
    "전제조건": "게임이 실행되지 않은 상태",
    "공통_재현절차_헤더": [
        "앱 실행",
        "로그인 화면 진입"
    ],
    "동등분할": {
        "ID": {
            "유효": ["testuser", "admin"],
            "무효": ["", "특수문자!@#"]
        },
        "PW": {
            "유효": ["test1234"],
            "무효": ["", "wrong"]
        }
    },
    "경계값": {
        "ID_길이": {
            "최소": 4,
            "최대": 20,
            "단위": "자"
        }
    },
    "결정테이블": [
        {
            "조건": {"ID": "유효", "PW": "유효"},
            "예상결과": "메인 화면 진입",
            "심각도": "Critical",
            "우선순위": "High"
        }
    ]
}
```

---

## 출력 형식

CSV + XLSX 동시 생성

### XLSX 시트 구성

| 시트 | 내용 |
|------|------|
| 전체 TC | 자동 생성된 테스트 케이스 |
| 사양 요약 | 기능명, 분류, 전제조건, 생성시각 |

### 출력 예시

| TC_ID | 테스트명 | 분류 | 심각도 |
|-------|---------|------|--------|
| TC-001 | ID 정상값 'testuser' 입력 시 동작 확인 | 로그인 | Medium |
| TC-002 | ID에 비정상값 '' 입력 시 오류 처리 확인 | 로그인 | High |
| TC-003 | ID_길이 최소 미만값(3자) 입력 시 오류 처리 확인 | 로그인 | High |
| TC-004 | ID_길이 최소값(4자) 입력 시 정상 동작 확인 | 로그인 | Medium |
| TC-005 | 정상 ID + 정상 PW 조합 시 동작 확인 | 로그인 | Critical |

---

## 빈 템플릿 생성

헤더만 있는 빈 TC 파일을 생성합니다.
직접 테스트 케이스를 작성할 때 사용합니다.

```bash
python main.py --template
```

### 생성되는 파일

```
결과/
├── tc_template.csv
└── tc_template.xlsx
```

---

## 도구 연동

```bash
# 1. TC 자동 생성
python 06.tc-generator/main.py

# 2. 생성된 TC 검증
python 02.data-validator/main.py 06.tc-generator/결과/testcases_로그인_latest.csv

# 3. QA 가 TC 실행 후 결과 컬럼 입력 (수동)

# 4. Fail TC 를 버그 리포트로 변환
python 03.md-report-gen/main.py 06.tc-generator/결과/testcases_로그인_latest.csv

# 5. 엑셀 종합 리포트
python 04.excel-reporter/main.py 03.md-report-gen/결과/bugs_latest.csv --all
```

---

## 유지보수 & 커스터마이즈 가이드

### 1. 새 기능 사양 추가

`specs/` 폴더에 JSON 파일만 추가하면 끝.

```bash
# specs/payment.json 작성 후
python main.py payment.json
```

### 2. 동등분할 값 추가

사양 JSON 의 유효/무효 리스트에 값 추가.

```json
"ID": {
    "유효": ["testuser", "admin", "newuser"],
    "무효": ["", "특수문자!@#", "공백 포함"]
}
```

### 3. 경계값 범위 변경

사양 JSON 의 최소/최대 수정.

```json
"ID_길이": {
    "최소": 4,
    "최대": 30,
    "단위": "자"
}
```

### 4. 결정 테이블 조합 추가

사양 JSON 의 결정테이블 리스트에 항목 추가.

```json
"결정테이블": [
    {"조건": {"ID": "유효", "PW": "유효"}, "예상결과": "..."},
    {"조건": {"ID": "유효", "PW": "무효"}, "예상결과": "..."},
    {"조건": {"새조건": "유효"}, "예상결과": "..."}
]
```

---

## 트러블슈팅

### 1. JSON 형식 오류

**해결**: JSON 검증 사이트(jsonlint.com)로 문법 확인

### 2. 한글 파일명 깨짐

**해결**: 모든 입출력에 `encoding="utf-8-sig"` 사용

---

## 기술 스택

| 기술 | 용도 |
|------|------|
| `json` | 사양 파일 로딩 |
| `csv` | CSV 출력 |
| `openpyxl` | XLSX 출력 |
| `pathlib` | 경로 관리 |
| `common.file_io` | 공통 입출력 |
| `common.excel_style` | 엑셀 스타일 |
| `common.logger` | 로깅 |