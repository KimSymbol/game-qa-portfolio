# 📱 2048 Mobile QA 자동화

오픈소스 Android 앱 [Privacy Friendly 2048](https://f-droid.org/packages/org.secuso.privacyfriendly2048/)을 대상으로
uiautomator2 + pytest 기반 모바일 자동화 테스트를 구현했다.

에뮬레이터와 실기기(갤럭시 Z 플립3)에서 **같은 코드로 검증**했고, 실패하면 Jira 티켓 생성과 Slack 알림까지 자동으로 이어지게 했다.

## 🎬 시연 영상

👉 [2048 Mobile QA 자동화 시연](https://youtu.be/1gs1ShVXCl8)

## 🛠️ 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| **언어** | Python 3.12 | - |
| **모바일 자동화** | uiautomator2 | resource-id 기반 UI 요소 접근 및 제스처 |
| **기기 제어** | ADB | 기기 연결, 앱 설치, 에뮬레이터 제어 |
| **이미지 비교** | Pillow, numpy | UI 속성으로 검증 불가한 영역 판정 |
| **화면 미러링** | scrcpy | 실기기 화면을 PC로 미러링하여 테스트 과정 확인 및 시연 녹화 |
| **테스트** | pytest | 테스트 실행 및 관리 |
| **리포트** | Allure | 스크린샷 포함 테스트 리포트 |
| **CI/CD** | GitHub Actions | self-hosted runner에서 에뮬레이터 부팅부터 자동화 |
| **버그 트래킹** | Jira REST API v3 | 실패 시 티켓 생성 + 중복 시 댓글 + 스크린샷 첨부 |
| **알림** | Slack Webhook (Block Kit) | 결과 요약 + 테스트 기기 정보 |
| **버그 리포트** | CSV/XLSX (openpyxl) | 02.tools 컬럼 구조 호환 |

## 🧪 테스트 설계

### 검증 수단의 이원화

이 프로젝트에서 가장 고민한 부분은 **무엇을 검증하느냐에 따라 수단을 다르게 가져간 것**이다.

앱 UI 계층을 덤프해 보니 점수·버튼은 `resource-id`로 접근할 수 있었지만, 게임 보드의 타일 하나하나는 커스텀 뷰로 그려져 UI 속성에 잡히지 않았다.

| 검증 대상 | 수단 | 선택 이유 |
|----------|------|----------|
| 화면 전환, 버튼 존재 | UI 속성 (`resource-id`) | 가장 정확하고 빠름 |
| 점수 증가 (병합) | UI 속성 (`points` 텍스트) | 값을 직접 읽을 수 있음 |
| 타일 이동 | 보드 영역 이미지 비교 | UI 속성 부재, 유일한 수단 |

이미지 비교는 **UI 속성으로는 도저히 확인이 안 될 때만** 쓴다는 선을 지켰다.

### 테스트 케이스

| ID | 분류 | 테스트명 | 절차 | 기대 결과 | 검증 수단 |
|----|------|---------|------|----------|----------|
| TW-001 | 앱 실행 | 메인 화면 표시 | 앱 실행 | 새 게임 버튼 존재 | UI 속성 |
| TW-002 | 앱 실행 | 새 게임 시작 | START NEW GAME 클릭 | 게임 화면 진입, 점수 0 | UI 속성 |
| TW-003 | 게임플레이 | 타일 이동 | 4방향 순회 스와이프 | 보드 이미지 변화 감지 | 이미지 비교 |
| TW-004 | 게임플레이 | 병합 시 점수 증가 | 병합까지 반복 스와이프 | 점수 증가 | UI 속성 |
| TW-005 | 게임플레이 | 재시작 시 초기화 | 재시작 버튼 클릭 | 점수 0으로 초기화 | UI 속성 |
| TW-006 | 화면 이동 | 뒤로가기 복귀 | Android 뒤로가기 키 | 메인 화면 표시 | 하드웨어 키 |
| TW-007 | 화면 이동 | 이어하기 상태 복원 | CONTINUE GAME 클릭 | 나가기 전 점수 복원 | UI 속성 |

### 테스트 설계 핵심 원칙

- **POM(Page Object Model)**: UI 요소 접근을 `GamePage` 클래스로 분리
- **3단 구조**: 각 테스트 파일을 변수 선언부 / 함수 선언부 / 메인 실행부로 구분하여 테스트 함수 본문은 헬퍼 호출 1~3줄로 유지
- **session scope fixture**: 앱 실행·게임 시작을 재사용하여 실행 시간 단축
- **환경변수 기반 기기 선택**: `DEVICE_SERIAL`로 에뮬레이터/실기기를 코드 수정 없이 전환
- **랜덤성 배제**: 타일 생성 위치가 랜덤이므로 단일 방향 검증 대신 4방향 순회로 재현성 확보

### PC 게임 자동화와의 비교

같은 포트폴리오의 [Flare RPG 프로젝트](../02.flare-rpg)와 나란히 놓고 보면 접근 방식의 차이가 뚜렷하다.

| 항목 | PC (Flare RPG) | 모바일 (2048) |
|------|---------------|--------------|
| 요소 탐지 | OpenCV 템플릿 매칭 | resource-id 조회 |
| 좌표 결정 | 이미지 매칭 결과에서 산출 | UI 요소의 bounds 속성 |
| 레이아웃 변경 대응 | 템플릿 재수집 필요 | 자동 대응 |
| 검증 정확도 | 픽셀 기반 (간접) | 속성 값 (직접) |
| 전체 실행 시간 | 약 2분 | 약 20초 |

## 📁 프로젝트 구조
```
03.2048-mobile/
├── apk/
│ └── org.secuso.privacyfriendly2048_100.apk # 테스트 대상 앱 (버전 고정)
├── pages/
│ └── game_page.py # POM - 앱 화면 제어
├── tests/
│ ├── test_1_launch.py # TW-001 ~ TW-002
│ ├── test_2_gameplay.py # TW-003 ~ TW-005
│ └── test_3_navigation.py # TW-006 ~ TW-007
├── utils/
│ ├── device_utils.py # 기기 연결, 이미지 비교, Allure 첨부
│ ├── jira_reporter.py # Jira 티켓 자동 생성 + 댓글 + 스크린샷
│ ├── bug_reporter.py # CSV/XLSX 버그 리포트 생성
│ └── slack_notifier.py # Slack Block Kit 결과 요약
├── conftest.py # fixture + 실패 리포팅 hook
├── pytest.ini
├── .env # 기기/Jira/Slack 설정 (.gitignore)
└── requirements.txt
```
## 🔧 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 전체 화면 비교 시 항상 '변화 있음'으로 판정 | 상태바 시계가 매초 갱신됨 | `number_field` 요소의 bounds로 보드 영역만 crop 후 비교 |
| 타일 값을 UI 속성으로 읽을 수 없음 | 보드가 커스텀 뷰로 직접 렌더링 | 이동은 이미지 비교, 병합은 `points` 텍스트로 검증 수단 이원화 |
| 화면 가장자리 스와이프가 뒤로가기로 동작 | Android 시스템 제스처와 충돌 | 앱이 제공하는 `touch_field` 영역 내부에서 스와이프 |
| 기기 두 대 연결 시 대상이 불확실 | `u2.connect()` 자동 선택 | `DEVICE_SERIAL` 환경변수로 대상 명시 |
| CI에서 adb 명령이 `more than one device` 오류 | 실기기가 USB 연결된 상태로 CI 실행 | 모든 adb 명령에 `-s` 시리얼 지정 |
| 부팅 중 `device offline`을 PowerShell이 실패로 처리 | 네이티브 명령의 stderr를 에러로 승격 | `$ErrorActionPreference = "Continue"` + `2>&1` 병합 |
| 로컬 통과, CI에서 TW-003 간헐적 실패 | 초기 타일이 이미 왼쪽 벽에 붙은 랜덤 배치 | 단일 방향 → 4방향 순회 검증으로 재설계 |

## 📱 검증 환경

| 환경 | 기기 | OS | 용도 |
|------|------|-----|------|
| 에뮬레이터 | Pixel 6 (AVD) | Android 14 | 개발 및 CI 실행 |
| 실기기 | 갤럭시 Z 플립3 (SM-F711N) | Android 15 | 실환경 검증 |

같은 테스트 코드로 양쪽 환경 모두 전체 통과했고, 대상은 환경변수만 바꿔 전환한다.

## ⚙️ 실행 방법

### 사전 준비

```bash
# 1. ADB 연결 확인
adb devices

# 2. 앱 설치
adb -s <시리얼> install -r apk/org.secuso.privacyfriendly2048_100.apk

# 3. uiautomator2 초기화
python -m uiautomator2 init --serial <시리얼>
```

### 로컬 실행

```bash
# venv 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# .env 파일에 대상 기기 지정
# DEVICE_SERIAL=emulator-5554   (에뮬레이터)
# DEVICE_SERIAL=R5CRB30GHGW     (실기기)

# 전체 테스트 실행
pytest tests/ -v -s --alluredir=allure-results

# Allure 리포트 확인
allure serve allure-results
```

### CI/CD

GitHub Actions self-hosted runner에서 자동 실행.

- 트리거: `01.game-automation/03.2048-mobile/` 변경 시 자동 + 수동 실행
- 에뮬레이터 자동 부팅 → 부팅 완료 대기 → APK 설치 → pytest → 에뮬레이터 종료
- 실패 시 Jira 티켓 자동 생성, Slack 결과 알림
- Allure 리포트 GitHub Pages 자동 배포

👉 [Allure 리포트 보기](https://kimsymbol.github.io/game-qa-portfolio/2048-mobile/)