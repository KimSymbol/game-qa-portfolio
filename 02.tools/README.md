# 🎮 Game QA Tools

게임 QA 업무 자동화를 위한 6가지 파이썬 도구 모음과 통합 파이프라인입니다.

ISTQB 기반 테스트 케이스 자동 생성부터 데이터 검증, 다양한 형식의 리포트 생성까지 — 게임 QA 워크플로우 전반을 자동화합니다.

---

## 🔗 파이프라인 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                    pipeline.py (통합 자동화)                │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────┐
│ 06.tc-generator      │   JSON 사양 → ISTQB 기반 TC 자동 생성
│ (테스트 케이스 설계) │   ├ 동등분할
└──────────────────────┘   ├ 경계값 분석
            │              └ 결정 테이블
            ▼
┌──────────────────────┐
│ 01.test-data-gen     │   QA + 기획 더미 데이터 9종
│ (더미 데이터 생성)   │   bugs / testcases / logs /
└──────────────────────┘   items / skills / monsters / ...
            │
            ▼
┌──────────────────────┐
│ 02.data-validator    │   JSON 규칙 기반 데이터 무결성 검증
│ (데이터 검증)        │   8가지 검사: 필수컬럼/빈값/허용값/
└──────────────────────┘   날짜/중복/패턴/범위/공백
            │
            ▼
┌──────────────────────┐
│ 03.md-report-gen     │   Fail 케이스 → 마크다운 버그 리포트
│ (마크다운 리포트)    │   개별 .md + 통합 ALL_BUGS.md
└──────────────────────┘
            │
            ▼
┌──────────────────────┐
│ 04.excel-reporter    │   5시트 엑셀 + JSON + HTML + PDF
│ (리포트 생성)        │   다양한 형식으로 통합 리포트
└──────────────────────┘
            │
            ▼
┌──────────────────────┐
│ 05.log-analyzer      │   서버 로그 분석 + 버그 이력 추적
│ (로그 분석)          │   신규/해결/중복 버그 자동 감지
└──────────────────────┘
```

---

## 🧰 도구 한눈에 보기


| #   | 도구                 | 역할                | 입력                   | 출력                    |
| --- | ------------------ | ----------------- | -------------------- | --------------------- |
| 01  | **test-data-gen**  | 더미 데이터 생성         | -                    | csv, txt              |
| 02  | **data-validator** | 데이터 무결성 검증        | csv, xlsx            | xlsx, json, html      |
| 03  | **md-report-gen**  | 마크다운 버그 리포트       | csv, xlsx            | md, csv               |
| 04  | **excel-reporter** | 통합 리포트 생성         | csv, xlsx, tsv, json | xlsx, json, html, pdf |
| 05  | **log-analyzer**   | 로그 분석             | txt, log             | xlsx, json, html      |
| 06  | **tc-generator**   | ISTQB 기반 TC 자동 생성 | json                 | csv, xlsx                   |


---

## 프로젝트 구조

```
02.tools/
├── pipeline.py                # 통합 자동화 스크립트
├── README.md                  # 이 파일
│
├── common/                    # 공통 모듈
│   ├── __init__.py            # 패키지 초기화
│   ├── file_io.py             # 다양한 입출력 형식 지원
│   ├── excel_style.py         # 엑셀 공통 스타일
│   ├── logger.py              # 로깅 시스템
│   ├── config.py              # 설정 로딩
│   ├── config.json            # 전역 설정
│   ├── column_mapper.py       # 외부 데이터 컬럼 매핑 변환
│   ├── column_map.json        # 매핑 규칙 설정
│   ├── convert.py             # 변환 실행 파일
│   └── README.md              # 공통 모듈 문서
│
├── 01.test-data-gen/          # 더미 데이터 생성
├── 02.data-validator/         # 데이터 무결성 검증
├── 03.md-report-gen/          # 마크다운 버그 리포트
├── 04.excel-reporter/         # 통합 리포트 생성
├── 05.log-analyzer/           # 로그 분석
├── 06.tc-generator/           # TC 자동 생성
│
└── logs/                      # 실행 로그 (.gitignore 제외, 자동 생성)
```

---

## ⚙️ 설치

## 설치

### 1. Python 환경 (3.8 이상 권장)

```bash
python --version
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

| 패키지 | 용도 |
|--------|------|
| `pandas` | csv/xlsx/json 입출력 |
| `openpyxl` | 엑셀 파일 생성/스타일 |
| `faker` | 한국어 더미 데이터 생성 |
| `reportlab` | PDF 리포트 생성 |
| `schedule` | 자동 스케줄러 |


---

## 🎬 시연 영상

QA Tools 시연

> 📺 [YouTube 전체 시연 영상 보기](https://youtu.be/J9GxlsjLduU)

**시연 내용**

- `pipeline.py` 한 번으로 6개 도구 자동 실행
- TC 자동 생성 → 데이터 검증 → 리포트 생성까지
- 다양한 출력 형식 (xlsx, json, html, pdf)

---

## 🚀 빠른 시작

### 한 번에 전체 실행 (추천)

```bash
cd 02.tools

# 전체 단계 자동 실행
python pipeline.py

# 모든 출력 형식 (xlsx + json + html + pdf) + 폴더 자동 오픈
python pipeline.py --all --open
```

### 단계별 실행

```bash
# 단계 2 (데이터 검증) 부터 시작
python pipeline.py --start-from 2

# 데이터 생성 건너뛰기 (기존 데이터 사용)
python pipeline.py --skip-gen --all
```

### 도움말

```bash
python pipeline.py --help
```

---

## 빈 템플릿 생성

각 도구에서 빈 파일을 생성해 직접 데이터를 입력할 수 있습니다.

```bash
# 데이터 입력용 빈 CSV/XLSX (bugs, testcases, items 등 9종)
python 01.test-data-gen/main.py --template

# 검증 규칙 JSON 템플릿
python 02.data-validator/main.py --template

# 버그 리포트 마크다운 템플릿
python 03.md-report-gen/main.py --template

# TC 작성용 빈 CSV/XLSX
python 06.tc-generator/main.py --template
```

---

## 외부 데이터 변환

다른 팀/프로젝트의 TC나 버그 데이터를 내부 형식으로 변환할 수 있습니다.
JSON 설정 파일로 매핑 규칙을 관리하며, 컬럼명 자동 추천 기능을 지원합니다.

```bash
# 매핑 목록 조회
python common/convert.py --list

# 매핑 초안 자동 생성 (컬럼명 자동 추천)
python common/convert.py external_tc.xlsx --generate 우리팀_TC

# 매핑 설정 검증
python common/convert.py --validate

# 변환 미리보기 (저장 없이 확인)
python common/convert.py external_tc.xlsx --map 우리팀_TC --preview

# 실제 변환 (CSV + XLSX 동시 생성)
python common/convert.py external_tc.xlsx --map 우리팀_TC

# 버그 데이터 변환도 가능
python common/convert.py jira_bugs.csv --map 예시_버그매핑
```

자세한 사용법과 변환 예시는 [common (공통 모듈)](./common/README.md) 을 참고하세요.

## 누락 컬럼 자동 보완

외부 데이터에 필수 컬럼이 없어도 도구가 자동으로 기본값을 채워서 동작합니다.

```
입력: TC_ID, 테스트명, 결과 (3개 컬럼만)
  ↓ 자동 보완
심각도(Medium), 상태(미해결), 플랫폼(PC) 등 누락 컬럼 자동 추가
  ↓
xlsx, json, html, pdf 정상 생성
```

## 필수 컬럼 커스터마이즈

특정 컬럼을 필수에서 제외하거나 기본값을 변경할 수 있습니다.

| 목적 | 수정 파일 | 수정 내용 |
|------|----------|----------|
| 검증 시 필수 해제 | `rules/*.json` | `필수_컬럼` 에서 제거 + `"필수": false` |
| 리포트 기본값 변경 | `reporter.py` | `필수컬럼_기본값` 딕셔너리 수정 |
| 마크다운 기본값 변경 | `md_generator.py` | `필수컬럼_기본값` 딕셔너리 수정 |
| 변환 시 컬럼 추가 안 함 | `column_map.json` | `내부_필수_컬럼` 에서 제거 |

예시: "발견자", "발견일" 을 안 쓰고 싶을 때

```bash
# 1. rules/testcases.json → 필수_컬럼 에서 제거 + "필수": false
# 2. reporter.py → 필수컬럼_기본값 에서 빈 값 유지 또는 제거
# 3. column_map.json → 내부_필수_컬럼 에서 제거
```

자세한 수정 방법은 각 도구의 README 를 참고하세요.

---

## 🛠️ 개발 순서 (도구가 만들어진 흐름)

각 도구는 다음 순서로 개발되었습니다.


| 순서  | 도구             | 개발 의도             |
| --- | -------------- | ----------------- |
| 1️⃣ | log-analyzer   | 로그 분석 자동화 기초 학습   |
| 2️⃣ | excel-reporter | 엑셀 리포트 자동 생성      |
| 3️⃣ | test-data-gen  | 테스트 데이터 자동 생성     |
| 4️⃣ | md-report-gen  | 버그 리포트 마크다운 자동화   |
| 5️⃣ | data-validator | 데이터 무결성 검증        |
| 6️⃣ | tc-generator   | ISTQB 기반 TC 자동 설계 |


> 💡 폴더 번호는 **파이프라인 실행 순서** 기준입니다.

---

## 💡 주요 특징

- ✅ **다양한 입출력 형식** — csv / tsv / xlsx / txt / log / json (입력) → xlsx / json / html / pdf (출력)
- ✅ **ISTQB 기반 TC 자동 생성** — 동등분할, 경계값 분석, 결정 테이블 자동화
- ✅ **공통 모듈 분리** — 모든 도구가 `common/` 모듈을 공유해서 유지보수 용이
- ✅ **JSON 규칙 기반 검증** — 코드 수정 없이 JSON 파일로 검증 규칙 관리
- ✅ **로깅 시스템** — 모든 도구의 실행 이력이 `logs/` 폴더에 자동 저장
- ✅ **이력 보존** — 모든 결과물에 타임스탬프 + `latest` 파일 자동 생성
- ✅ **한글 완벽 지원** — `utf-8-sig` 통일로 엑셀/메모장에서 한글 안 깨짐
- ✅ **통합 파이프라인** — 단일 명령어로 6개 도구 자동 실행

---

## 🛠️ 트러블슈팅

도구를 개발하면서 만났던 주요 이슈와 해결 방법입니다.

### 1. 엑셀에서 한글 깨짐

**증상**

```
csv 파일을 엑셀로 열면 한글이 ?로 표시
```

**원인**
Excel은 BOM 없는 UTF-8을 자동 인식 못 함

**해결**

```python
# 모든 csv 쓰기에 utf-8-sig 사용
with open(파일명, "w", newline="", encoding="utf-8-sig") as f:
    ...
```

---

### 2. 모듈 import 실패

**증상**

```
ImportError: cannot import name '...' from 'common.file_io'
```

**원인**
`sys.path.append()` 는 검색 우선순위가 낮아서 다른 같은 이름 모듈이 먼저 로딩됨

**해결**

```python
# append → insert(0, ...) 으로 변경
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

### 3. 병합 셀 (MergedCell) 에러

**증상**

```
AttributeError: 'MergedCell' object attribute 'value' is read-only
```

**원인**
`for 셀 in ws.columns` 로 순회 시 병합 셀 객체에서 에러 발생

**해결**

```python
from openpyxl.utils import get_column_letter

for i, 열 in enumerate(ws.columns, 1):
    열이름 = get_column_letter(i)  # 인덱스로 열 이름 가져오기
    ...
```

---

### 4. ModuleNotFoundError (캐시 문제)

**증상**

```
ModuleNotFoundError: No module named 'common'
또는
AttributeError: module '...' has no attribute '...'
```

**원인**
Python이 `__pycache__` 안의 이전 버전을 로딩

**해결**

```bash
# __pycache__ 폴더 삭제
Remove-Item -Recurse -Force __pycache__
```

---

### 5. 와일드카드 `*` 가 인식 안 됨 (PowerShell)

**증상**

```
❌ 파일이 없어요: bugs_*.csv
```

**원인**
PowerShell은 `*` 와일드카드를 셸 레벨에서 처리하지 않음 (bash와 다름)

**해결**

```bash
# latest 파일 사용
python 02.data-validator/main.py 01.test-data-gen/결과/bugs_latest.csv

# 또는 폴더 지정
python 02.data-validator/main.py 01.test-data-gen/결과/
```

---

### 6. BOM 문자가 첫 컬럼명에 붙음

**증상**

```python
df.columns
# ['\ufeff버그ID', '제목', ...]
```

**원인**
`utf-8-sig` 로 저장된 파일을 `utf-8` 로 읽음

**해결**

```python
# 읽기도 utf-8-sig 로 통일
df = pd.read_csv(경로, encoding="utf-8-sig")
```

---

### 7. 경로 탐색 실패

**증상**

```
❌ 파일이 없어요: 02.excel-reporter/03.test-data-gen/결과/bugs.csv
```

**원인**
도구가 자기 폴더 기준으로만 상대 경로를 탐색

**해결**

```python
# 다중 경로 탐색
def 파일_읽기(파일명, 기준경로=None):
    경로 = Path(파일명)
    # 1. cwd 또는 절대 경로
    if not 경로.exists() and 기준경로:
        # 2. 기준경로(도구 폴더) 기준
        경로 = Path(기준경로) / 파일명
    ...
```

---

### 8. 차트의 라벨이 표시되지 않음

**증상**
openpyxl 차트를 만들었는데 데이터 레이블이 안 보임

**원인**
openpyxl 의 차트 데이터 레이블 지원 제약

**해결**
차트 대신 **색상 구분 테이블** 사용

```python
# 데이터를 표로 표시하면서 셀 배경색으로 시각적 구분
for 행 in 데이터:
    ws.append(행)
    행_색상(ws, ws.max_row, 색상_가져오기(행["심각도"]))
```

---

### 9. 함수를 못 찾는 AttributeError

**증상**

```
AttributeError: module 'md_generator' has no attribute '리포트_생성'
```

**원인**
파일 저장 안 됐거나, 함수 추가가 누락됨

**해결**

```bash
# 함수가 실제로 있는지 확인
python -c "import md_generator; print(dir(md_generator))"
```

---

## 🏗️ 기술 스택


| 분류            | 기술                   |
| ------------- | -------------------- |
| **언어**        | Python 3.8+          |
| **데이터 처리**    | pandas, csv, json    |
| **엑셀**        | openpyxl             |
| **PDF**       | reportlab            |
| **더미 데이터**    | faker (ko_KR, en_US) |
| **로깅**        | logging              |
| **정규표현식**     | re                   |
| **테스트 설계 기법** | ISTQB CTFL / CT-GaMe |


---

## 📂 결과물 확인

각 도구를 실행하면 도구별 `결과/` 폴더에 결과물이 저장됩니다.

```
01.test-data-gen/결과/      # bugs_*.csv, testcases_*.csv, logs_*.txt, ...
02.data-validator/결과/     # validation_report_*.xlsx/json/html
03.md-report-gen/결과/      # bug_reports/*.md, ALL_BUGS.md, bugs_*.csv
04.excel-reporter/결과/     # report_*.xlsx/json/html/pdf
05.log-analyzer/결과/       # bug_report_*.xlsx/json/html, bug_history.json
06.tc-generator/결과/       # testcases_*_*.csv
```

> 💡 각 파일은 **타임스탬프 + latest** 두 가지 형식으로 자동 생성됩니다.

---

## 📝 개별 도구 사용법

각 도구의 자세한 사용법은 해당 폴더의 `README.md` 를 참고하세요.

- [common (공통 모듈)](./common/README.md)
- [01.test-data-gen](./01.test-data-gen/README.md)
- [02.data-validator](./02.data-validator/README.md)
- [03.md-report-gen](./03.md-report-gen/README.md)
- [04.excel-reporter](./04.excel-reporter/README.md)
- [05.log-analyzer](./05.log-analyzer/README.md)
- [06.tc-generator](./06.tc-generator/README.md)