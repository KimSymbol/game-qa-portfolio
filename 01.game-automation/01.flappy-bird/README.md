# 🐦 Flappy Bird QA 자동화

오픈소스 Flappy Bird 클론([FlapPyBird](https://github.com/sourabhv/FlapPyBird))을
대상으로 PyAutoGUI + OpenCV + pytest 기반 자동화 테스트를 구현했습니다.

## 🎬 시연 영상

👉 [YouTube에서 보기](https://youtu.be/gc4bCL45jqw)

## 🛠️ 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| **언어** | Python 3.12 | - |
| **이미지 인식** | OpenCV | 템플릿 매칭으로 게임 화면 상태 감지 |
| **입력 제어** | pydirectinput | pygame 이벤트 루프에 키 입력 전달 |
| **창 제어** | pygetwindow, pywin32 | 게임 창 탐지 및 포커스 이동 |
| **테스트** | pytest | 테스트 실행 및 관리 |
| **리포트** | Allure | 스크린샷 포함 테스트 리포트 생성 |
| **CI/CD** | GitHub Actions | self-hosted runner로 자동 테스트 실행 |

## 🧪 테스트 설계

### 테스트 대상 화면 흐름
```
게임 실행
↓
시작 대기 화면 (Get Ready!)
↓
TAP → 게임 플레이
↓
충돌/추락 → 게임오버
↓
TAP → 재시작
```

### 테스트 케이스

| ID | 테스트명 | 전제조건 | 테스트 단계 | 기대 결과 |
|----|---------|---------|------------|---------|
| FB-001 | 시작화면 표시 | 게임 실행 | 시작 화면 요소 확인 | title, get_ready, tap 템플릿 발견 |
| FB-002 | 게임 시작 | 시작 대기 화면 | TAP 입력 | get_ready 사라짐 |
| FB-003 | 게임오버 화면 표시 | 게임 플레이 중 | 추락 대기 | gameover 템플릿 발견 |
| FB-004 | 게임오버 후 재시작 | 게임오버 화면 | TAP 입력 | 시작 화면 복귀 |

### 테스트 설계 핵심 원칙

- **POM(Page Object Model)**: 화면 제어 로직을 `GamePage` 클래스로 분리
- **커스텀 Wait**: `time.sleep` 대신 템플릿 감지 기반 대기로 안정성 향상
- **session scope fixture**: 테스트 간 게임 상태를 이어받아 자연스러운 플레이 사이클 재현

## 📁 프로젝트 구조
```
01.flappy-bird/
├── assets/
│   └── templates/          # OpenCV 템플릿 이미지
│       ├── title.png
│       ├── get_ready.png
│       ├── tap.png
│       └── gameover.png
├── pages/
│   └── game_page.py        # POM - 게임 화면 제어
├── tests/
│   ├── test_1_start.py     # FB-001, FB-002
│   └── test_2_gameover.py  # FB-003, FB-004
├── utils/
│   └── screen_utils.py     # 캡처, 템플릿 매칭, Wait 함수
├── conftest.py             # pytest fixture
└── requirements.txt
```

## 🔧 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 한글 경로에서 이미지 로드 실패 | `cv2.imread()` 한글 경로 미지원 | `np.fromfile()` + `cv2.imdecode()` 로 우회 |
| 낮/밤 배경 변화로 템플릿 매칭 실패 | 배경색이 바뀌어 유사도 저하 | 실제 캡처 이미지에서 템플릿 재추출 |
| pytest 실행 중 키 입력 안됨 | `pyautogui` 가 pygame 이벤트 루프에 전달 안됨 | `pydirectinput` 으로 교체 |
| 창 가려짐으로 캡처 실패 | `pyautogui` 는 화면에 보이는 것만 캡처 | `PrintWindow` API로 직접 캡처 |
| CI/CD 에서 게임 창 못 띄움 | runner 서비스가 Session 0 에서 실행 | 시작프로그램으로 사용자 세션에서 실행 |

## ⚙️ 실행 방법

### 로컬 실행

```bash
# 1. venv 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. FlapPyBird 실행 (별도 터미널)
cd FlapPyBird
python main.py

# 4. 테스트 실행
cd 01.flappy-bird
pytest tests/ -v --alluredir=allure-results

# 5. Allure 리포트 확인
allure serve allure-results
```

### CI/CD

GitHub main 브랜치에 push 하면 자동으로 실행돼요.

👉 [Allure 리포트 보기](https://kimsymbol.github.io/game-qa-portfolio)
