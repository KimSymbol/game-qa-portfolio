# 🎲 Test Data Generator

QA 테스트에 필요한 더미 데이터를 자동으로 생성하는 도구입니다.
실제 테스트 환경과 유사한 데이터를 빠르게 만들 수 있습니다.

---

## 📁 프로젝트 구조

```
03.test-data-gen/
├── generator.py     # 핵심 생성 모듈
├── main.py          # 실행 파일
├── README.md
└── 결과/
    ├── bugs_YYYY-MM-DD.csv
    ├── logs_YYYY-MM-DD.txt
    ├── users_YYYY-MM-DD.csv
    ├── testcases_YYYY-MM-DD.csv
    ├── characters_YYYY-MM-DD.csv
    └── server_response_YYYY-MM-DD.csv
```

---

## ⚙️ 설치

```bash
pip install faker
```

---

## 🚀 실행 방법

```bash
# 전체 데이터 기본 건수로 생성
python main.py

# 전체 데이터 50건으로 생성
python main.py 50

# 특정 데이터만 생성
python main.py bugs        # 버그 리포트 (기본 20건)
python main.py logs        # 게임 로그 (기본 50줄)
python main.py users       # 유저 계정 (기본 30건)
python main.py testcases   # 테스트 케이스 (기본 20건)
python main.py characters  # 캐릭터 스탯 (기본 30건)
python main.py server      # 서버 응답 (기본 100건)

# 건수 지정
python main.py bugs 100
python main.py server 500
```

---

## 📄 생성 데이터 형식

### 버그 리포트 (bugs_YYYY-MM-DD.csv)

| 컬럼 | 형식 | 예시 |
|------|------|------|
| 버그ID | BUG-001 | BUG-001 |
| 제목 | 문자열 | 캐릭터가 벽을 통과함 |
| 심각도 | Critical / High / Medium / Low | Critical |
| 우선순위 | High / Medium / Low | High |
| 플랫폼 | PC / Android / iOS | PC |
| 버전 | v1.X.XX | v1.2.34 |
| 상태 | 미해결 / 진행중 / 해결 | 해결 |
| 발견자 | 한국어 이름 | 홍길동 |
| 발견일 | YYYY-MM-DD | 2026-06-10 |
| 해결일 | YYYY-MM-DD (해결 시) | 2026-06-12 |
| 재현율 | N/10 | 8/10 |

> excel-reporter 도구로 바로 분석 가능한 형식

### 게임 로그 (logs_YYYY-MM-DD.txt)

```
ERROR: 캐릭터 충돌 감지 BUG-001 at 14:30:22
WARNING: 메모리 사용량 80% at 14:31:05
INFO: 서버 연결 정상
```

> log-analyzer 도구로 바로 분석 가능한 형식

### 테스트 케이스 (testcases_YYYY-MM-DD.csv)

| 컬럼 | 형식 | 예시 |
|------|------|------|
| TC_ID | TC-001 | TC-001 |
| 테스트명 | 문자열 | 정상 로그인 확인 |
| 분류 | 로그인/인벤토리 등 | 로그인 |
| 결과 | Pass / Fail / Block / Skip | Fail |
| 심각도 | Fail일 때만 | Critical |

> md-report-gen 도구의 입력 파일로 바로 사용 가능

### 서버 응답 (server_response_YYYY-MM-DD.csv)

| 응답시간 | 판정 |
|---------|------|
| 200ms 미만 | 🟢 정상 |
| 200~500ms | 🟡 경고 |
| 500ms 이상 | 🔴 위험 |

---

## 🛠️ 기술 스택

| 기술 | 용도 |
|------|------|
| `faker` | 실감나는 가짜 데이터 생성 |
| `csv` | CSV 파일 생성 |
| `random` | 랜덤 데이터 선택 |
| `datetime` | 날짜 데이터 생성 |
| `pathlib` | 경로 관리 |