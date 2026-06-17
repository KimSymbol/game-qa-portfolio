# 📊 Excel Bug Reporter

버그 데이터 CSV 파일을 입력하면
자동으로 전문적인 4시트 엑셀 리포트를 생성하는 도구입니다.

---

## 📁 프로젝트 구조

```
02.excel-reporter/
├── bugs.csv          # 입력 데이터 (기본값)
├── reporter.py       # 핵심 모듈
├── main.py           # 실행 파일
├── README.md
└── 결과/
    └── report_YYYY-MM-DD.xlsx
```

---

## ⚙️ 설치

```bash
pip install pandas openpyxl
```

---

## 🚀 실행 방법

```bash
# 1. 기본 파일 (bugs.csv) 분석
python main.py

# 2. 파일 지정
python main.py june_bugs.csv

# 3. 파일 여러 개 → 리포트도 여러 개 생성
python main.py june.csv july.csv

# 4. 폴더 지정 → 안의 csv 파일 전부 리포트 생성
python main.py data/
```

> 상위 폴더에서 실행할 때
> ```bash
> python 02.excel-reporter/main.py
> python 02.excel-reporter/main.py data/
> ```

---

## 📄 CSV 파일 형식

### 필수 컬럼

| 컬럼명 | 형식 | 예시 | 필수 여부 |
|--------|------|------|----------|
| 버그ID | 문자열 | BUG-001 | ✅ 필수 |
| 제목 | 문자열 | 캐릭터 벽 통과 | ✅ 필수 |
| 심각도 | Critical / Major / Minor | Critical | ✅ 필수 |
| 담당자 | 문자열 | 홍길동 | ✅ 필수 |
| 상태 | 해결 / 진행중 / 미해결 | 해결 | ✅ 필수 |
| 발견일 | YYYY-MM-DD | 2026-06-10 | ✅ 필수 |
| 해결일 | YYYY-MM-DD | 2026-06-12 | ⬜ 선택 |

### 예시

```csv
버그ID,제목,심각도,담당자,상태,발견일,해결일
BUG-001,캐릭터 벽 통과,Critical,홍길동,해결,2026-06-10,2026-06-12
BUG-002,인벤토리 아이템 사라짐,Major,이철수,진행중,2026-06-11,
BUG-003,사운드 끊김,Minor,홍길동,해결,2026-06-11,2026-06-13
BUG-004,서버 응답 없음,Critical,박영희,미해결,2026-06-12,
```

### 규칙

- 첫 번째 줄은 반드시 헤더
- 인코딩: UTF-8
- 해결일은 미해결/진행중이면 비워도 됨
- 심각도는 반드시 `Critical` / `Major` / `Minor` 중 하나
- 상태는 반드시 `해결` / `진행중` / `미해결` 중 하나

---

## 📊 엑셀 리포트 구성

| 시트 | 내용 |
|------|------|
| 전체 버그 목록 | 심각도별 색상 구분 전체 목록 |
| 담당자별 현황 | 담당자별 버그 현황 + 막대 차트 |
| 심각도별 통계 | Critical🔴 / Major🟡 / Minor🟢 집계 |
| 요약 대시보드 | 해결률 등 핵심 지표 한눈에 보기 |

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `pandas` | CSV 읽기 및 데이터 분석 |
| `openpyxl` | 엑셀 생성 / 스타일 / 차트 |
| `pathlib` | 경로 관리 / 폴더 자동 생성 |
| `datetime` | 날짜별 파일명 자동 생성 |