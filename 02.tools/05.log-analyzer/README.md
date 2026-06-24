# 🔍 Log Analyzer

게임 서버 로그를 자동으로 분석하고 **버그 이력을 추적**하는 도구입니다.
신규/해결/중복 버그를 자동 감지하고 5시트 엑셀 + JSON + HTML 리포트를 생성합니다.

---

## 📁 프로젝트 구조

```
05.log-analyzer/
├── qa_tools.py        # 핵심 모듈
├── main.py            # 실행 파일
├── scheduler.py       # 자동 스케줄러
├── bug_log.txt        # 기본 샘플 로그
├── README.md
└── 결과/              # ⚠️ .gitignore 로 제외됨 (실행 시 자동 생성)
    ├── bug_report_YYYY-MM-DD_HH-MM-SS.xlsx
    ├── bug_report_YYYY-MM-DD_HH-MM-SS.json
    ├── bug_report_YYYY-MM-DD_HH-MM-SS.html
    ├── bug_report_latest.{xlsx,json,html}
    └── bug_history.json  # 이력 추적용
```

> 💡 `결과/` 폴더는 `.gitignore` 에 추가되어 있어 GitHub 에 올라가지 않습니다.

---

## ⚙️ 설치

```bash
pip install openpyxl schedule
```

---

## 🚀 실행 방법

```bash
# 기본 파일 (bug_log.txt) 분석
python main.py

# 파일 지정
python main.py error.log

# 여러 파일
python main.py a.txt b.log

# 폴더 안 txt/log 전부
python main.py logs/

# 모든 출력 형식 (xlsx + json + html)
python main.py --all

# 자동 스케줄러 (매일 09:00 자동 실행)
python scheduler.py
```

---

## 📄 로그 파일 형식 (.txt / .log)

### 기본 형식
```
[로그유형]: [내용] [버그ID] at [시간]
```

### 예시
```
ERROR: 캐릭터 충돌 BUG-001 at 14:30:22
INFO: 서버 연결 정상
WARNING: 메모리 사용량 80%
ERROR: 서버 응답 없음 BUG-007 at 16:00:11
```

### 심각도 자동 분류

| 심각도 | 키워드 |
|--------|--------|
| Critical | 충돌, crash, 서버 다운, 응답 없음 |
| High | 프레임 드랍, 렉, 지연, 오류 |
| Medium | 경고, warning, 메모리 |
| Low | 기본값 (키워드 매칭 없을 때) |

---

## 📊 출력 리포트 (5시트 XLSX)

| 시트 | 내용 |
|------|------|
| 전체 로그 | ERROR/WARNING/INFO 색상 구분 |
| 버그 리포트 | Critical / High / Medium / Low 심각도 분류 |
| 통계 요약 | 유형별 건수 |
| 변경 사항 | 신규/해결 버그 (이전 실행과 비교) |
| 중복 버그 | 반복 발생 버그 감지 |

> 💡 `bug_history.json` 으로 **이전 실행과 비교**하여 신규/해결 버그 자동 추적

---

## 🔗 도구 연동

```bash
# 1. test-data-gen 으로 로그 생성
python 01.test-data-gen/main.py logs

# 2. log-analyzer 로 분석
python 05.log-analyzer/main.py 01.test-data-gen/결과/logs_latest.txt --all
```

---

## 🔧 유지보수 & 커스터마이즈 가이드

### 1. 심각도 분류 키워드 추가

`qa_tools.py` 의 `심각도_분류()` 함수 내 키워드맵만 수정.

```python
키워드맵 = {
    "Critical": ["충돌", "crash", "서버 다운", "응답 없음", "치명적"],
    "High"    : ["프레임 드랍", "렉", "지연", "오류"],
    "Medium"  : ["경고", "warning", "메모리"],
}
```

### 2. 로그 형식 변경

`qa_tools.py` 의 `버그정보_추출()` 함수에서 정규표현식 수정.

```python
def 버그정보_추출(로그):
    버그ID = re.search(r"BUG-\d+", 로그)      # 예: BUG-001
    시간   = re.search(r"\d{2}:\d{2}:\d{2}", 로그)  # 예: 14:30:22

    # 형식 변경 예시: ERROR-001 패턴으로
    # 버그ID = re.search(r"ERROR-\d+", 로그)
```

### 3. 스케줄러 실행 시간 변경

`scheduler.py` 에서 시간만 수정.

```python
# 매일 09:00 → 매일 18:00
schedule.every().day.at("18:00").do(분석_실행)

# 1시간마다 실행
schedule.every(1).hours.do(분석_실행)
```

---

## 🛠️ 트러블슈팅

### 1. bug_history.json 이 중복 생성돼요

**원인**: 결과 폴더가 여러 개

**해결**: 같은 도구는 항상 자기 `결과/` 폴더만 사용

### 2. .log 파일이 인식 안 돼요

**해결**: `common/file_io.py` 의 `파일_읽기()` 가 `.txt` 와 `.log` 동시 지원

```python
elif 확장자 in [".txt", ".log"]:
    ...
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `re` | 정규표현식 (버그ID/시간 추출) |
| `json` | 버그 히스토리 저장 |
| `collections.Counter` | 중복 카운팅 |
| `schedule` | 자동 스케줄러 |
| `openpyxl` | 엑셀 리포트 |
| `common.file_io` | 공통 입출력 |
| `common.excel_style` | 엑셀 스타일 |
| `common.logger` | 로깅 |