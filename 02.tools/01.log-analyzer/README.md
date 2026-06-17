# 🔍 Log Analyzer

로그 파일을 읽어 버그를 자동 분류하고
색상 구분된 5시트 엑셀 리포트를 생성하는 도구입니다.

---

## 📁 프로젝트 구조

```
01.log-analyzer/
├── bug_log.txt          # 분석할 로그 파일 (기본값)
├── qa_tools.py          # 핵심 분석 모듈
├── main.py              # 실행 파일
├── scheduler.py         # 자동 실행 스케줄러
├── README.md
└── 결과/
    ├── bug_report_YYYY-MM-DD.xlsx   # 엑셀 리포트
    └── bug_history.json             # 이전 실행 히스토리
```

---

## ⚙️ 설치

```bash
pip install openpyxl schedule
```

---

## 🚀 실행 방법

```bash
# 1. 기본 파일 (bug_log.txt) 분석
python main.py

# 2. 파일 지정
python main.py today_log.txt

# 3. 파일 여러 개
python main.py a.txt b.txt c.txt

# 4. 폴더 지정 → 안의 txt 파일 전부 분석
python main.py logs/

# 5. 자동 스케줄러 실행 (매일 09:00 자동 분석)
python scheduler.py
```

> 상위 폴더에서 실행할 때
> ```bash
> python 01.log-analyzer/main.py
> python 01.log-analyzer/main.py logs/
> ```

---

## 📄 로그 파일 형식 (.txt)

### 기본 형식
```
[로그유형]: [내용] [버그ID] at [시간]
```

### 예시
```
ERROR: 캐릭터 충돌 BUG-001 at 14:30:22
INFO: 서버 연결 정상
WARNING: 메모리 사용량 80%
ERROR: 프레임 드랍 BUG-042 at 15:10:05
INFO: 데이터 로딩 완료
ERROR: 서버 응답 없음 BUG-007 at 16:00:11
```

### 규칙

| 항목 | 형식 | 필수 여부 |
|------|------|----------|
| 로그 유형 | `ERROR` / `WARNING` / `INFO` | ✅ 필수 |
| 버그 ID | `BUG-숫자` (예: BUG-001) | ⬜ 선택 |
| 발생 시간 | `HH:MM:SS` (예: 14:30:22) | ⬜ 선택 |
| 인코딩 | UTF-8 | ✅ 필수 |
| 확장자 | `.txt` | ✅ 필수 |

> 버그 ID / 시간이 없으면 엑셀에 "없음" 으로 표시됩니다.

### 심각도 자동 분류 키워드

| 심각도 | 키워드 |
|--------|--------|
| 🔴 Critical | 충돌, crash, 서버 다운, 응답 없음 |
| 🟡 Major | 프레임 드랍, 렉, 지연, 오류 |
| 🟢 Minor | 경고, warning, 메모리 |

---

## 📊 엑셀 리포트 구성

| 시트 | 내용 |
|------|------|
| 전체 로그 | ERROR🔴 / WARNING🟡 / INFO🟢 색상 구분 |
| 버그 리포트 | Critical🔴 / Major🟡 / Minor🟢 심각도 분류 |
| 통계 요약 | 유형별 버그 건수 집계 |
| 변경 사항 | 신규🔴 / 해결✅ 버그 추적 |
| 중복 버그 | 반복 발생 버그🟡 감지 |

---

## 🔗 도구 연동

`test-data-gen` 으로 생성한 로그 파일을 바로 분석할 수 있어요.

```bash
# 1. test-data-gen 으로 로그 생성
python 03.test-data-gen/main.py logs

# 2. 생성된 로그 파일 분석
python 01.log-analyzer/main.py 03.test-data-gen/결과/logs_2026-06-17.txt
```

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `re` | 버그 ID / 시간 정규표현식 추출 |
| `pathlib` | 경로 관리 / 폴더 자동 생성 |
| `openpyxl` | 엑셀 리포트 자동 생성 |
| `json` | 버그 히스토리 저장 |
| `datetime` | 날짜별 파일명 자동 생성 |
| `collections` | 중복 버그 카운팅 |
| `schedule` | 자동 실행 스케줄러 |