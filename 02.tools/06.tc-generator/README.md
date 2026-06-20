# 🧪 Test Case Generator

JSON 사양 파일을 기반으로 
테스트 케이스를 자동 생성하는 도구입니다.

---

## 📁 프로젝트 구조

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
└── 결과/              # ⚠️ .gitignore 로 제외됨 (실행 시 자동 생성)
    ├── testcases_로그인_YYYY-MM-DD_HH-MM-SS.csv
    ├── testcases_로그인_YYYY-MM-DD_HH-MM-SS.xlsx
    ├── testcases_로그인_latest.csv
    ├── testcases_로그인_latest.xlsx
    └── ...
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
# specs/ 폴더 전체 사양으로 TC 생성
python main.py

# 특정 사양 1개
python main.py login.json

# 여러 사양
python main.py login.json shop.json
```

---

## 🎓 ISTQB 테스트 설계 기법 3가지

| 기법 | 설명 | TC 생성 방식 |
|------|------|-------------|
| **동등분할** | 같은 결과 나오는 입력 그룹 | 유효/무효 그룹당 1개씩 |
| **경계값 분석** | 경계에서 버그 확률 높음 | 최소-1, 최소, 최대, 최대+1 |
| **결정 테이블** | 조건 조합 시나리오 | 조건 조합마다 1개씩 |

---

## 📄 JSON 사양 파일 형식

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

## 📊 출력 파일

### CSV 출력
- 03.md-report-gen, 02.data-validator 와 호환되는 형식

### XLSX 출력 (3시트)

| 시트 | 내용 |
|------|------|
| 전체 TC | 모든 TC (기법별 색상 구분) |
| 기법별 통계 | 동등분할/경계값/결정테이블 비율 |
| 사양 요약 | 기능명/분류/전제조건/생성시각 |

---

## 🔗 도구 연동

```bash
# 1. TC 자동 생성
python 06.tc-generator/main.py

# 2. 생성된 TC 검증
python 02.data-validator/main.py 06.tc-generator/결과/testcases_로그인_latest.csv --all

# 3. QA 가 TC 실행 후 결과 컬럼 입력
# (수동 작업)

# 4. Fail TC 를 버그 리포트로 변환
python 03.md-report-gen/main.py 06.tc-generator/결과/testcases_로그인_latest.csv

# 5. 엑셀 종합 리포트
python 04.excel-reporter/main.py 03.md-report-gen/결과/bugs_latest.csv --all
```

---

## 🔧 유지보수 & 커스터마이즈 가이드

### 1. 새 기능 사양 추가 (가장 흔한 케이스)

`specs/` 폴더에 JSON 파일만 추가하면 끝.

```bash
# specs/payment.json 작성 후
python main.py payment.json    # 자동 인식
```

#### specs/payment.json 예시

```json
{
    "기능명": "결제",
    "분류": "결제",
    "전제조건": "로그인 + 상점 진입",
    "공통_재현절차_헤더": ["로그인", "상점 진입"],
    "동등분할": {
        "결제수단": {
            "유효": ["카드", "계좌이체", "휴대폰"],
            "무효": ["만료카드", "잔액부족"]
        }
    },
    "경계값": {
        "결제_금액": {
            "최소": 100,
            "최대": 1000000,
            "단위": "원"
        }
    },
    "결정테이블": [
        {
            "조건": {"결제수단": "유효", "결제_금액": "유효"},
            "예상결과": "결제 성공",
            "심각도": "Critical",
            "우선순위": "High"
        }
    ]
}
```

### 2. 새 테스트 설계 기법 추가

#### Step 1. `tc_generator.py` 에 기법 함수 추가

```python
def 상태전이_TC_생성(사양):
    """상태 전이 기법 (State Transition)"""
    TC목록 = []
    상태전이 = 사양.get("상태전이", [])

    for 전이 in 상태전이:
        TC목록.append({
            "기법": "상태전이",
            "테스트명": f"[상태전이] {전이['전']} → {전이['후']}",
            ...
        })

    return TC목록
```

#### Step 2. `전체_TC_생성()` 에 호출 추가

```python
전체 = 동등분할_TC + 경계값_TC + 결정테이블_TC + 상태전이_TC  # ← 추가
```

### 3. XLSX 시트 추가

`XLSX_저장()` 함수에 시트 함수 추가 + 호출.

```python
# 새 시트 추가
ws4 = wb.create_sheet(title="상세 분석")
ws4.append(["..."])
열너비_조정(ws4)
```

---

## 🛠️ 트러블슈팅

### 1. JSON 형식 오류

**증상**: `JSONDecodeError`

**해결**: JSON 검증 사이트(jsonlint.com)로 문법 확인

### 2. 정규표현식 문자열 이스케이프

**증상**: 패턴이 작동 안 함

**해결**: JSON 에서 `\d` 는 `\\d` 로 두 번 이스케이프

```json
{
    "패턴": "BUG-\\d+"
}
```

### 3. 한글 폴더명 깨짐

**해결**: 모든 입출력에 `encoding="utf-8"` 또는 `utf-8-sig` 사용

---


## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `json` | 사양 파일 로딩 |
| `csv` | CSV 출력 |
| `openpyxl` | XLSX 출력 |
| `pathlib` | 경로 관리 |
| `datetime` | 타임스탬프 |
| `common.file_io` | 공통 입출력 |
| `common.excel_style` | 엑셀 스타일 |
| `common.logger` | 로깅 |