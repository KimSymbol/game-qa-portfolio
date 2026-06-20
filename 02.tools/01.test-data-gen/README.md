# 🎲 Test Data Generator

QA 테스트에 필요한 **9종의 더미 데이터**를 자동으로 생성하는 도구입니다.
한국어/영어 페이커(faker)와 게임 도메인 데이터를 조합해 현실감 있는 데이터를 만듭니다.

---

## 📁 프로젝트 구조

```
01.test-data-gen/
├── generator.py    # 핵심 모듈 (9종 데이터 생성 함수)
├── main.py         # 실행 파일
├── README.md
└── 결과/           # ⚠️ .gitignore 로 제외됨 (실행 시 자동 생성)
    ├── bugs_YYYY-MM-DD_HH-MM-SS.csv
    ├── bugs_latest.csv
    ├── logs_YYYY-MM-DD_HH-MM-SS.txt
    ├── testcases_YYYY-MM-DD_HH-MM-SS.csv
    └── ... (각 종류마다 타임스탬프 + latest 파일)
```

> 💡 `결과/` 폴더는 `.gitignore` 에 추가되어 있어 GitHub 에 올라가지 않습니다.
> 도구를 처음 실행하면 자동 생성됩니다.

---

## ⚙️ 설치

```bash
pip install pandas openpyxl faker
```

---

## 🚀 실행 방법

```bash
# 전체 데이터 기본 건수로 생성
python main.py

# 전체 데이터 N건씩 생성
python main.py 50

# 특정 종류만 생성
python main.py bugs            # 버그 리포트 20건 (기본)
python main.py testcases 30    # 테스트 케이스 30건
python main.py items 100       # 아이템 100건
```

---

## 📋 생성 가능한 데이터 9종

### QA 관련 데이터

| 종류 | 명령어 | 기본 건수 | 출력 형식 |
|------|--------|---------|---------|
| 버그 리포트 | `bugs` | 20 | csv |
| 게임 로그 | `logs` | 50 | txt |
| 유저 계정 | `users` | 30 | csv |
| 테스트 케이스 | `testcases` | 20 | csv |
| 캐릭터 스탯 | `characters` | 30 | csv |
| 서버 응답 | `server` | 100 | csv |

### 기획 관련 데이터

| 종류 | 명령어 | 기본 건수 | 출력 형식 |
|------|--------|---------|---------|
| 아이템 | `items` | 50 | csv |
| 스킬 | `skills` | 30 | csv |
| 몬스터 | `monsters` | 30 | csv |

---

## 📄 데이터 예시

### bugs.csv

| 버그ID | 제목 | 심각도 | 우선순위 | 플랫폼 | 상태 | 발견자 | 발견일 |
|--------|------|--------|---------|--------|------|--------|--------|
| BUG-001 | 캐릭터가 벽을 통과함 | Critical | High | PC | 미해결 | 김상진 | 2026-03-15 |
| BUG-002 | 인벤토리 아이템이 사라짐 | High | Medium | Android | 진행중 | 이영희 | 2026-04-22 |

### testcases.csv

| TC_ID | 테스트명 | 분류 | 결과 | 심각도 | 플랫폼 |
|-------|---------|------|------|--------|--------|
| TC-001 | 정상 로그인 확인 | 로그인 | Pass | | PC |
| TC-002 | 아이템 구매 후 인벤토리 반영 | 인벤토리 | Fail | High | iOS |

### items.csv

| 아이템ID | 이름 | 타입 | 등급 | 가격 | 공격력 |
|---------|------|------|------|------|-------|
| ITEM-0001 | 전설 검 | 무기 | 전설 | 100000 | 4500 |
| ITEM-0002 | 일반 갑옷 | 방어구 | 일반 | 100 | 0 |

---

## 🔗 도구 연동

생성된 데이터는 다른 도구의 입력으로 바로 사용할 수 있습니다.

```bash
# 1. 데이터 생성
python 01.test-data-gen/main.py

# 2. 데이터 검증
python 02.data-validator/main.py 01.test-data-gen/결과/bugs_latest.csv --all

# 3. 마크다운 버그 리포트
python 03.md-report-gen/main.py 01.test-data-gen/결과/testcases_latest.csv

# 4. 엑셀 리포트
python 04.excel-reporter/main.py 03.md-report-gen/결과/bugs_latest.csv --all

# 5. 로그 분석
python 05.log-analyzer/main.py 01.test-data-gen/결과/logs_latest.txt --all
```

---

## 💡 설계 포인트

- ✅ **한국어 + 영어 페이커** 동시 사용 (이름은 한국어, 이메일은 영어)
- ✅ **게임 도메인 데이터** 풀 직접 정의 (직업, 맵, 아이템 종류 등)
- ✅ **타임스탬프 + latest** 파일 동시 생성으로 이력 보존
- ✅ **utf-8-sig 인코딩** 통일로 엑셀 한글 깨짐 방지
- ✅ **현실감 있는 데이터 분포** (등급별 가격 차등, 직업별 스탯 등)

---

## 📊 데이터 생성 로직 예시

### 아이템 가격 (등급별 차등)

```python
등급배율 = {"일반": 1, "고급": 3, "희귀": 10, "영웅": 30, "전설": 100}
가격 = random.randint(100, 1000) * 등급배율[등급]
```

### 캐릭터 스탯 (직업별)

```python
직업스탯 = {
    "전사" : ((800, 1200), (100, 300), ...),    # HP 높음, MP 낮음
    "마법사": ((400, 700), (500, 1000), ...),   # HP 낮음, MP 높음
}
배율 = 1 + (레벨 / 100)
캐릭터HP = int(random.randint(*직업스탯[직업][0]) * 배율)
```

---

## 🔧 유지보수 & 커스터마이즈 가이드

이 도구는 **쉽게 확장하거나 수정**할 수 있도록 설계되었습니다.

### 1. 데이터 풀 수정 (이름, 직업, 맵 등)

`generator.py` 상단의 데이터 풀을 수정하면 모든 함수에 자동 반영됩니다.

```python
# generator.py 상단
직업목록      = ["전사", "마법사", "궁수", "도적", "성직자"]
맵목록        = ["초원", "던전", "설원", "사막", "화산"]
아이템타입목록 = ["무기", "방어구", "소비", "재료", "장신구"]

# → 직업 추가하고 싶으면 리스트에 한 줄만 추가
직업목록 = ["전사", "마법사", "궁수", "도적", "성직자", "암살자"]  # ← 추가
```

---

### 2. 기본 생성 건수 변경

`main.py` 의 `기본건수맵` 딕셔너리만 수정하면 됩니다.

```python
# main.py
기본건수맵 = {
    "bugs"      : 20,    # ← 숫자만 변경
    "testcases" : 50,    # 기본값을 20 → 50 으로 변경
    ...
}
```

---

### 3. 새로운 데이터 종류 추가하기

#### Step 1. `generator.py` 에 생성 함수 추가

```python
def 퀘스트_생성(건수=30):
    """퀘스트 데이터 더미를 CSV로 생성"""
    폴더   = 결과폴더_생성(기준경로)
    시각   = 타임스탬프()
    파일명 = 폴더 / f"quests_{시각}.csv"

    헤더 = ["퀘스트ID", "이름", "타입", "보상골드", "보상경험치"]
    데이터 = []
    for i in range(1, 건수 + 1):
        데이터.append([
            f"QST-{i:04d}",
            f"퀘스트 {i}",
            random.choice(["메인", "서브", "일일"]),
            random.randint(100, 10000),
            random.randint(50, 5000),
        ])

    CSV_쓰기(파일명, 헤더, 데이터)
    Latest_복사(파일명, "quests")
    return 파일명
```

#### Step 2. `main.py` 의 매핑 딕셔너리에 추가

```python
생성함수맵 = {
    # ... 기존 ...
    "quests": generator.퀘스트_생성,    # ← 추가
}

기본건수맵 = {
    # ... 기존 ...
    "quests": 30,                       # ← 추가
}
```

#### Step 3. 끝! 바로 실행 가능

```bash
python main.py quests       # 퀘스트 30건 생성
python main.py quests 100   # 100건 생성
```

---

### 4. CSV 형식 변경 (인코딩, 구분자 등)

`generator.py` 의 `CSV_쓰기` 함수만 수정하면 모든 데이터에 일괄 적용됩니다.

```python
def CSV_쓰기(파일명, 헤더, 데이터):
    # 예: TSV로 바꾸고 싶다면
    with open(파일명, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter="\t")  # ← 구분자만 변경
        writer.writerow(헤더)
        writer.writerows(데이터)
```

---

## 🛠️ 트러블슈팅

### 1. 엑셀에서 한글이 깨져요

**원인**: utf-8 으로만 저장하면 Excel 이 인식 못 함

**해결**: `utf-8-sig` (BOM 포함) 인코딩 사용

```python
with open(파일명, "w", newline="", encoding="utf-8-sig") as f:
    ...
```

---

### 2. `_latest` 파일이 없어요

**원인**: `Latest_복사` 함수 미적용

**해결**: `common/file_io.py` 의 `Latest_복사` 함수 추가 후 각 생성 함수 마지막에 호출

```python
from common.file_io import Latest_복사

def 버그리포트_생성(건수=20):
    # ... 데이터 생성 ...
    CSV_쓰기(파일명, 헤더, 데이터)
    Latest_복사(파일명, "bugs")  # ← 추가
    return 파일명
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `faker` | 한국어/영어 더미 데이터 (이름, 이메일 등) |
| `random` | 게임 도메인 데이터 무작위 조합 |
| `csv` | CSV 파일 입출력 |
| `pathlib` | 경로 관리 |
| `datetime` | 타임스탬프 생성 |
| `common.file_io` | 공통 입출력 모듈 |
| `common.logger` | 로깅 시스템 |