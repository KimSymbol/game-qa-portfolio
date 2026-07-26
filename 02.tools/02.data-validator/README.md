# 📋 Data Validator

CSV/XLSX 파일의 **데이터 무결성을 자동으로 검사**하는 도구.
검사 항목은 JSON 규칙 파일로 관리하고, 규칙 파일이 없어도 기본 검사는 돌아간다.

---

## 📁 프로젝트 구조

```
02.data-validator/
├── validator.py         # 핵심 모듈 (8가지 검사 + 다중 출력)
├── main.py              # 실행 파일
├── README.md
├── rules/               # 검사 규칙 설정 파일
│   ├── bugs.json        # 버그 데이터 검사 규칙
│   ├── testcases.json   # 테스트 케이스 검사 규칙
│   ├── items.json       # 아이템 기획 데이터 검사 규칙
│   ├── skills.json      # 스킬 기획 데이터 검사 규칙
│   ├── monsters.json    # 몬스터 기획 데이터 검사 규칙
│   └── default.json     # 기본 규칙
└── 결과/                # ⚠️ .gitignore 로 제외됨 (실행 시 자동 생성)
    ├── validation_report_YYYY-MM-DD_HH-MM-SS.xlsx
    ├── validation_report_YYYY-MM-DD_HH-MM-SS.json
    ├── validation_report_YYYY-MM-DD_HH-MM-SS.html
    └── validation_report_latest.xlsx (+json/html)
```

> 💡 `결과/` 폴더는 `.gitignore` 에 추가되어 있어 GitHub 에 올라가지 않는다.
> 도구를 처음 실행하면 자동 생성된다.

---

## ⚙️ 설치

```bash
pip install pandas openpyxl
```

---

## 🚀 실행 방법

```bash
# 파일 지정 (XLSX 만 생성, 기본)
python main.py bugs.csv

# 모든 출력 형식 (xlsx + json + html)
python main.py bugs.csv --all

# 특정 형식만
python main.py bugs.csv --json
python main.py bugs.csv --html

# 폴더 안 csv/xlsx 전부 검증
python main.py data/
```

---

## 빈 규칙 템플릿 생성

새 데이터의 검증 규칙을 만들 때 사용할 JSON 템플릿을 생성.

```bash
python main.py --template
```

### 사용 방법

1. `rules/template.json` 이 생성된다
2. 복사해서 이름 변경 (예: `quests.json`)
3. `필수_컬럼`, `컬럼_규칙` 을 데이터에 맞게 수정
4. `validator.py` 의 `매핑목록` 에 키워드 추가

### 템플릿 구조

```json
{
    "설명": "데이터 검사 규칙 (이 설명을 수정하세요)",
    "필수_컬럼": ["컬럼1", "컬럼2"],
    "컬럼_규칙": {
        "컬럼1_ID": {
            "필수": true,
            "중복불가": true,
            "패턴": "PREFIX-\\d+"
        },
        "컬럼2_타입": {
            "허용값": ["값1", "값2", "값3"]
        },
        "컬럼3_날짜": {
            "날짜형식": "%Y-%m-%d"
        },
        "컬럼4_숫자": {
            "최소값": 0,
            "최대값": 99999
        }
    }
}
```

---

## 📋 검사 항목 8가지

| 검사 | 설명 | 규칙 파일 필요? |
|------|------|---------------|
| 필수컬럼 | 필수 컬럼 존재 여부 | ✅ 필요 |
| 빈값 | 필수 항목 누락 | 🔶 없으면 전체 검사 |
| 허용값 | 오타/잘못된 값 (예: "Critcal") | ✅ 필요 |
| 날짜형식 | 날짜 형식 오류 | ✅ 필요 |
| 중복 | 중복 데이터 | 🔶 없으면 전체 행 검사 |
| 패턴 | 정규표현식 패턴 불일치 | ✅ 필요 |
| 범위 | 숫자 값 범위 검사 (기획 데이터용) | ✅ 필요 |
| 공백 | 앞뒤 공백 오류 | ❌ 항상 검사 |

---

## 📄 규칙 파일 자동 매핑

파일 이름에 따라 자동으로 규칙 파일을 선택한다.

| 파일 이름에 포함 | 사용되는 규칙 |
|-----------------|-------------|
| `bugs` | `rules/bugs.json` |
| `testcases` | `rules/testcases.json` |
| `items` | `rules/items.json` |
| `skills` | `rules/skills.json` |
| `monsters` | `rules/monsters.json` |
| 그 외 | `rules/default.json` |
| 전부 없음 | 내장 기본 규칙 (빈값/중복/공백만) |

---

## 📄 규칙 파일 형식

### bugs.json 예시

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

| 속성 | 값 예시 | 설명 |
|------|--------|------|
| `필수` | true/false | 빈 값 허용 여부 |
| `중복불가` | true/false | 중복 값 허용 여부 |
| `허용값` | ["A", "B"] | 허용되는 값 목록 |
| `날짜형식` | "%Y-%m-%d" | 날짜 형식 |
| `패턴` | "BUG-\\\\d+" | 정규표현식 패턴 |
| `최소값` | 0 | 숫자 범위 검사 |
| `최대값` | 99999 | 숫자 범위 검사 |

---

## 📊 출력 형식

| 형식 | 용도 |
|------|------|
| **xlsx** | 시트 2개 (전체 오류 + 유형별 요약) |
| **json** | 자동화 파이프라인 연동 |
| **html** | 웹 브라우저 / 메일 첨부 |

### XLSX 시트 구성

| 시트 | 내용 |
|------|------|
| 오류 목록 | 전체 오류 상세 (유형별 색상 구분) |
| 요약 | 검사 유형별 통과/실패 현황 |

---

## 🔗 도구 연동

```bash
# 1. test-data-gen 으로 데이터 생성
python 01.test-data-gen/main.py bugs

# 2. data-validator 로 데이터 검증
python 02.data-validator/main.py 01.test-data-gen/결과/bugs_latest.csv --all

# 3. 검증 통과 후 excel-reporter 로 리포트 생성
python 04.excel-reporter/main.py 01.test-data-gen/결과/bugs_latest.csv --all
```

### tc-generator 와 연동

```bash
# 1. tc-generator 로 TC 자동 생성
python 06.tc-generator/main.py

# 2. 생성된 TC 검증
python 02.data-validator/main.py 06.tc-generator/결과/testcases_로그인_latest.csv --all
```

---

## 💡 설계 포인트

- ✅ **JSON 규칙 파일 기반** — 코드 수정 없이 검사 규칙 관리
- ✅ **파일명 자동 매핑** — 파일 이름으로 규칙 자동 선택
- ✅ **8가지 검사 항목** — 필수컬럼/빈값/허용값/날짜/중복/패턴/범위/공백
- ✅ **다중 출력 형식** — xlsx + json + html
- ✅ **타임스탬프 + latest** — 이력 보존
- ✅ **기획 데이터 지원** — 아이템/스킬/몬스터 범위 검사

---

## 🔧 유지보수 & 커스터마이즈 가이드

### 1. 새 검사 규칙 추가 (가장 흔한 케이스)

`rules/` 폴더에 JSON 파일만 추가하면 된다.

#### Step 1. `rules/quests.json` 생성

```json
{
    "설명": "퀘스트 기획 데이터 검사 규칙",
    "필수_컬럼": ["퀘스트ID", "이름", "타입", "보상골드"],
    "컬럼_규칙": {
        "퀘스트ID": {
            "필수": true,
            "중복불가": true,
            "패턴": "QST-\\d+"
        },
        "타입": {
            "필수": true,
            "허용값": ["메인", "서브", "일일"]
        },
        "보상골드": {
            "필수": true,
            "최소값": 0,
            "최대값": 9999999
        }
    }
}
```

#### Step 2. `validator.py` 의 매핑 키워드 추가

```python
# validator.py 의 규칙_로딩() 함수 안
매핑목록 = {
    "bugs"     : "bugs.json",
    "testcases": "testcases.json",
    "items"    : "items.json",
    "skills"   : "skills.json",
    "monsters" : "monsters.json",
    "quests"   : "quests.json",   # ← 추가
}
```

#### Step 3. 끝! 바로 실행 가능

```bash
python main.py quests.csv  # 자동으로 quests.json 규칙 적용
```

---

### 2. 새로운 검사 항목 추가 (예: 이메일 형식 검사)

#### Step 1. `validator.py` 에 검사 함수 추가

```python
import re

def 이메일_검사(df, 규칙):
    """이메일 형식 검사 (예시)"""
    오류목록 = []
    컬럼규칙 = 규칙.get("컬럼_규칙", {})

    for 컬럼, 설정 in 컬럼규칙.items():
        if not 설정.get("이메일", False) or 컬럼 not in df.columns:
            continue

        이메일패턴 = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        for idx, 행 in df.iterrows():
            값 = str(행[컬럼]).strip()
            if 값 == "" or 값 == "nan":
                continue
            if not re.fullmatch(이메일패턴, 값):
                오류목록.append({
                    "유형": "이메일",
                    "행": idx + 2,
                    "컬럼": 컬럼,
                    "값": 값,
                    "내용": f"{idx+2}행 '{컬럼}' 값 '{값}' 이 이메일 형식이 아님"
                })

    return 오류목록
```

#### Step 2. `검증_실행()` 함수에 추가

```python
전체오류 += 이메일_검사(df, 규칙)
```

#### Step 3. 규칙 JSON 에 사용

```json
"이메일": {
    "필수": true,
    "이메일": true
}
```

---

### 3. 검사 규칙 수정 (예: 새 심각도 추가)

`rules/bugs.json` 의 허용값만 수정하면 된다.

```json
"심각도": {
    "허용값": ["Critical", "High", "Medium", "Low", "Trivial"]   // ← Trivial 추가
}
```

---

### 4. HTML 리포트 스타일 변경

`common/file_io.py` 의 `HTML_쓰기` 함수 내부 CSS 만 수정하면
모든 도구의 HTML 출력에 일괄 반영된다.

```python
# common/file_io.py
def HTML_쓰기(파일경로, 제목, 본문):
    HTML = f"""<!DOCTYPE html>
    ...
    <style>
        body {{
            font-family: 'Malgun Gothic', sans-serif;  /* ← 폰트 변경 */
            ...
        }}
    </style>
    """
```

### 필수 컬럼 변경

특정 컬럼을 필수에서 제외하거나 추가할 수 있다.

#### 필수에서 제외 (예: "발견자" 제외)

`rules/testcases.json` 수정:

```json
{
    "필수_컬럼": [
        "TC_ID", "테스트명", "분류"
    ],
    "컬럼_규칙": {
        "발견자": {
            "필수": false
        }
    }
}
```

#### 필수로 추가 (예: "버전" 필수화)

```json
{
    "필수_컬럼": [
        "TC_ID", "테스트명", "분류", "버전"
    ],
    "컬럼_규칙": {
        "버전": {
            "필수": true
        }
    }
}
```



---

## 🛠️ 트러블슈팅

### 1. 규칙 파일을 못 찾음

**증상**
```
[WARN] 규칙 파일 없음 → 기본 규칙으로 검사
```

**원인**: 파일명에 매핑 키워드가 없음

**해결**
```bash
# 파일 이름 확인
# bugs_xxx.csv → bugs.json 매핑 ✅
# my_data.csv  → default.json 사용 (또는 매핑 키워드 추가)
```

---

### 2. BOM 문자가 컬럼명에 붙음

**증상**: 첫 번째 컬럼명이 `\ufeff버그ID` 로 표시

**원인**: utf-8-sig 로 저장된 파일을 utf-8 로 읽음

**해결**
```python
# 읽기도 utf-8-sig 로 통일
df = pd.read_csv(경로, encoding="utf-8-sig")
```

---

### 3. 패턴 검사가 안 됨

**증상**: `"패턴": "BUG-\d+"` 작성했는데 작동 안 함

**원인**: JSON 에서 `\d` 는 `\\d` 로 두 번 이스케이프 해야 함

**해결**
```json
{
    "패턴": "BUG-\\d+"
}
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `pandas` | CSV/XLSX 읽기 및 데이터 분석 |
| `openpyxl` | 검증 리포트 엑셀 생성 |
| `re` | 정규표현식 패턴 검사 |
| `json` | 규칙 파일 / 출력 |
| `pathlib` | 경로 관리 |
| `datetime` | 날짜 형식 검사 |
| `common.file_io` | 공통 입출력 모듈 |
| `common.excel_style` | 엑셀 공통 스타일 |
| `common.logger` | 로깅 시스템 |