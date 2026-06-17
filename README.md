# 🎮 Game QA Automation Portfolio

게임 QA 자동화 포트폴리오입니다.
PC 게임 및 모바일 게임을 대상으로 자동화 테스트를 구현했습니다.

## 📁 프로젝트 구조
```
game-qa-portfolio/
├── .github/workflows...  # 깃허브 액션 CI/CD 설정
├── 01.game-automation/
│    ├── 01.flappy-bird/  # Flappy Bird QA 자동화
│    └── 02.flare-rpg/    # Flare Rpg QA 자동화
├── 02.tools/             # QA 도구 모음
├── 03.추가 예정          # 분석서, 테스트케이스 등(추가 예정)
└── .gitmodules           # 서브 모듈 (FlapPybird)
```

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| **언어** | Python 3.12 |
| **게임 자동화** | PyAutoGUI · pydirectinput · OpenCV · pywin32 |
| **테스트** | pytest · Allure |
| **데이터 분석** | re · pandas · openpyxl |
| **CI/CD** | GitHub Actions (self-hosted runner) |
| **리포트** | Allure Report (GitHub Pages 자동 배포) |

## 📊 프로젝트 목록

### 🎮 01. Game Automation

| # | 프로젝트 | 기술 스택 | 상태 |
|---|---------|----------|------|
| 01 | [Flappy Bird QA 자동화](./01.game-automation/01.flappy-bird) | PyAutoGUI · OpenCV · pytest · Allure | ✅ 완료 |
| 02 | [Flare RPG QA 자동화](./01.game-automation/02.flare-rpg) | PyAutoGUI · OpenCV · pytest · Allure | ✅ 완료 |

### 🛠️ 02. Tools

| # | 프로젝트 | 기술 스택 | 상태 |
|---|---------|----------|------|
| 01 | [로그 자동 분석 시스템](./02.tools/01.log-analyzer) | re · openpyxl · schedule · json | ✅ 완료 |

## 🔗 Allure 리포트

👉 [GitHub Pages에서 보기](https://kimsymbol.github.io/game-qa-portfolio)

## 🎬 시연 영상

👉 [Flappy Bird QA 자동화 테스트](https://youtu.be/gc4bCL45jqw)

## 📋 팀 프로젝트 경험

### AI 헬피챗 QA 자동화 (부트캠프 팀 프로젝트)

| 항목 | 내용 |
|------|------|
| **대상 서비스** | AI 헬피챗 웹 서비스 |
| **기술 스택** | Selenium · pytest · GitLab CI/CD · Allure · Jira API |
| **주요 구현** | 회원가입(SI) · 로그인(LI) · 수업지도안(TS) 플로우 UI 자동화 |
| **특이사항** | Jira REST API v3 연동으로 버그 티켓 자동 생성 및 중복 방지 처리 |