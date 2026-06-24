# 🗡️ Flare RPG QA 자동화

오픈소스 PC RPG 게임 [Flare RPG](https://flarerpg.org/)를 대상으로 
PyAutoGUI + OpenCV + pytest 기반 자동화 테스트를 구현했습니다.

게임 시작부터 캐릭터 생성, 이동, 인벤토리, 전투, 사망 후 재시작까지 
**전체 플레이 사이클을 자동화**한 포트폴리오 프로젝트입니다.

## 🎬 시연 영상

👉 [YouTube에서 보기](https://youtu.be/SkB1OpMsIvU)

## 🛠️ 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| **언어** | Python 3.12 | - |
| **이미지 인식** | OpenCV | 템플릿 매칭으로 게임 화면 상태 감지 |
| **입력 제어** | pydirectinput, pyautogui | 키 입력, 마우스 클릭/드래그 |
| **창 제어** | pywin32 | 게임 창 탐지 및 포커스 이동 |
| **테스트** | pytest | 테스트 실행 및 관리 |
| **리포트** | Allure | 스크린샷 포함 테스트 리포트 생성 |
| **CI/CD** | GitHub Actions | self-hosted runner로 자동 테스트 실행 |
| **버그 트래킹** | Jira REST API v3 | 실패 시 자동 티켓 생성 + 중복 시 댓글 추가 + 스크린샷 첨부 |
| **알림** | Slack Webhook (Block Kit) | 테스트 결과 요약 알림 |
| **버그 리포트** | CSV/XLSX (openpyxl) | 02.tools 컬럼 호환 자동 생성 |

## 🧪 테스트 설계

### 테스트 대상 화면 흐름
```
게임 실행
↓
메인메뉴 (Play Game)
↓
세이브 선택 화면 (세이브 있을 때)
↓
캐릭터 생성 (Create)
↓
스토리 씬 → 로딩 → 튜토리얼 대화
↓
플레이 화면 (이동/인벤토리/전투)
↓
사망 → Continue → 재시작
```

### 테스트 케이스

| ID | 분류 | 테스트명 | 전제조건 | 테스트 단계 | 기대 결과 |
|----|------|---------|---------|------------|---------|
| FR-001 | 게임 시작 | 메인메뉴 표시 | 게임 실행 | 메인메뉴 요소 확인 | logo, play_game 발견 |
| FR-002 | 게임 시작 | Play Game 클릭 | 메인메뉴 | Play Game 버튼 클릭 | 다음 화면 이동 (세이브 유무 분기) |
| FR-003 | 게임 시작 | 캐릭터 생성 화면 | 세이브 선택 화면 | Delete Save → Yes → New Game | 캐릭터 생성 화면 표시 |
| FR-004 | 이동 | 캐릭터 이동 | 플레이 가능 상태 | S 키로 아래쪽 이동 | 미니맵 픽셀 변화 감지 |
| FR-005 | 인벤토리 | 인벤토리 열기 | 플레이 가능 상태 | I 키 입력 | 인벤토리 창 표시 |
| FR-006 | 인벤토리 | 아이템 장착/해제 | 인벤토리 열림 | 드래그로 해제 → 우클릭 장착 | 슬롯 상태 변화 |
| FR-007 | 인벤토리 | 인벤토리 닫기 | 인벤토리 열림 | I 키 입력 | 인벤토리 창 사라짐 |
| FR-008 | 전투 | 몬스터 공격 | 몬스터 근처 | 좌클릭 공격 | 몬스터 체력 감소 |
| FR-009 | 전투 | 피격 | 전투 중 | 좀비 공격 대기 | 캐릭터 체력 감소 |
| FR-010 | 재시작 | 게임오버 후 재시작 | 게임오버 화면 | Continue 클릭 | 플레이 화면 복귀 |

### 테스트 설계 핵심 원칙

- **POM(Page Object Model)**: 화면 제어 로직을 `GamePage` 클래스로 분리
- **session scope fixture**: 테스트 간 게임 상태를 이어받아 자연스러운 플레이 사이클 재현
- **slow 마커 활용**: 전투/재시작 테스트에 `@pytest.mark.slow` 적용 → 빠른 테스트만 선택 실행 가능
- **템플릿 자동 탐지**: 좌표 하드코딩 대신 `find_template_location()` 으로 위치 자동 탐지
- **픽셀 차이 비교**: 미니맵/체력바 영역 비교로 이동/전투/피격 감지

## 📁 프로젝트 구조
```
02.flare-rpg/
├── assets/
│   └── templates/              # OpenCV 템플릿 이미지 (16개)
├── pages/
│   └── game_page.py            # POM - 게임 화면 제어
├── tests/
│   ├── test_1_start.py         # FR-001 ~ FR-003
│   ├── test_2_movement.py      # FR-004
│   ├── test_3_inventory.py     # FR-005 ~ FR-007
│   ├── test_4_combat.py        # FR-008 ~ FR-009 (slow)
│   └── test_5_gameover.py      # FR-010 (slow)
├── utils/
│   ├── screen_utils.py         # 캡처, 템플릿 매칭, Wait 함수
│   ├── jira_reporter.py        # Jira 티켓 자동 생성 + 댓글 + 스크린샷 첨부
│   ├── bug_reporter.py         # CSV/XLSX 버그 리포트 자동 생성
│   └── slack_notifier.py       # Slack Block Kit 결과 요약 알림
├── conftest.py                 # pytest fixture (session scope) + hook
├── pytest.ini                  # pytest 설정 (slow 마커 등록)
├── .env                        # Jira/Slack/게임경로 환경변수 (.gitignore)
└── requirements.txt
```

## 🔧 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| Windows PC 보호 매번 뜸 | 다른 PC에서 다운로드한 실행파일로 인식 | 파일 속성에서 차단 해제 체크 |
| 클릭이 위쪽으로 빗나감 | `GetWindowRect` 가 상단바 포함 좌표 반환 | 상단바(31px) + 테두리(8px) 좌표 보정 |
| Play Game 클릭 후 화면이 달라짐 | 세이브 유무에 따라 다음 화면 분기 | 세이브 선택 화면 / 캐릭터 생성 화면 모두 처리 |
| 대화창 화살표 호버 시 매칭 실패 | 마우스 호버로 버튼 색상이 변함 | 클릭 후 마우스를 화면 좌측 상단으로 이동 |
| 좀비 위치가 매번 달라서 공격 좌표 불안정 | 좀비가 움직이는 몬스터 | 좀비가 다가올 때까지 대기 후 고정 좌표 공격 |
| 몬스터 체력바가 호버 시에만 표시 | 마우스 호버 유무에 따라 UI 표시 | 마우스 호버 유지 상태로 공격 전후 체력바 비교 |

## ⚙️ 실행 방법

### 로컬 실행

```bash
# 1. venv 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. Flare RPG 실행 (게임은 별도로 설치 필요)

# 4. 게임을 메인메뉴 상태로 두고 테스트 실행
pytest tests/ -v --alluredir=allure-results

# 5. slow 테스트 제외 실행 (빠른 테스트만)
pytest tests/ -v -m "not slow"

# 6. slow 테스트만 실행
pytest tests/ -v -m slow

# 7. Allure 리포트 확인
allure serve allure-results
```

### CI/CD

GitHub Actions self-hosted runner 로 자동 실행됩니다.

- 트리거: `01.game-automation/02.flare-rpg/` 폴더 변경 시 자동 + 수동 실행 가능
- 게임 자동 실행 + 알림창 자동 처리 + pytest 실행 + Allure 리포트 GitHub Pages 배포
- 실패 시 Jira 티켓 자동 생성, Slack 결과 알림

👉 [Allure 리포트 보기](https://kimsymbol.github.io/game-qa-portfolio/flare-rpg/)