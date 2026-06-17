# 🔍 QA 버그 자동 분석 시스템

Python으로 만든 QA 자동화 도구입니다.  
로그 파일을 읽어 버그를 자동 분류하고, 색상 구분된 엑셀 리포트를 생성합니다.

---

## 📁 프로젝트 구조
```
qa_project/
├── bug_log.txt       # 분석할 로그 파일
├── qa_tools.py       # QA 도구 모듈
├── main.py           # 메인 실행 파일
├── scheduler.py      # 자동 실행 스케줄러
├── README.md         # 프로젝트 설명
└── 결과/
├── bug_report_YYYY-MM-DD.xlsx
└── bug_history.json
```

---

## ⚙️ 설치

```bash
pip install openpyxl schedule
```

---

## 🚀 실행 방법

```bash
# 기본 실행
python main.py

# 파일 지정 실행
python main.py today_log.txt

# 자동 스케줄러 실행
python scheduler.py
```

---

## 📊 엑셀 리포트 구성

| 시트 | 내용 |
|------|------|
| 전체 로그 | ERROR🔴 / WARNING🟡 / INFO🟢 색상 구분 |
| 버그 리포트 | Critical🔴 / Major🟡 / Minor🟢 심각도 분류 |
| 통계 요약 | 유형별 버그 건수 집계 |
| 변경 사항 | 신규🔴 / 해결✅ 버그 추적 |
| 중복 버그 | 반복 발생 버그 감지🟡 |

---

## 🛠️ 사용 기술

| 기술 | 용도 |
|------|------|
| `re` | 버그 ID / 시간 정규표현식 추출 |
| `pathlib` | 경로 관리 / 폴더 자동 생성 |
| `openpyxl` | 엑셀 리포트 자동 생성 |
| `json` | 버그 히스토리 저장 |
| `datetime` | 날짜별 파일명 자동 생성 |
| `schedule` | 자동 실행 스케줄러 |
| `collections` | 중복 버그 카운팅 |

---

## 📝 로그 파일 형식
```
ERROR: 캐릭터 충돌 BUG-001 at 14:30:22
INFO: 서버 연결 정상
WARNING: 메모리 사용량 80%
```

---

## 🏆 최종 실행 결과
```
🔍 [bug_log.txt] 분석 시작...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
총 로그 수    : 8건
ERROR         : 3건 🔴
WARNING       : 2건 🟡
INFO          : 3건 🟢
버그 ID 목록  : ['BUG-001', 'BUG-042', 'BUG-007']
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 중복 버그 없음
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆕 신규 버그  : ['BUG-001', 'BUG-042', 'BUG-007']
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 결과 저장 완료: ...bug_report_2026-06-17.xlsx
```