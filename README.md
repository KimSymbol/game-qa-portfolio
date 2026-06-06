# 🎮 Game QA Automation Portfolio

게임 QA 자동화 포트폴리오입니다.
PC 게임 및 모바일 게임을 대상으로 자동화 테스트를 구현했습니다.

## 📁 프로젝트 구조
```
game-qa-portfolio/
├── 01.game-automation/
│   └── 01.flappy-bird/   # Flappy Bird QA 자동화
└── 02.분석서/             # 게임 분석 문서 (예정)
```

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| **언어** | Python 3.12 |
| **PC 자동화** | PyAutoGUI, pydirectinput, OpenCV, pygetwindow |
| **테스트** | pytest, Allure |
| **CI/CD** | GitHub Actions (self-hosted runner) |
| **리포트** | Allure Report (GitHub Pages 자동 배포) |

## 📊 프로젝트 목록

| # | 프로젝트 | 플랫폼 | 상태 |
|---|---------|--------|------|
| 01 | [Flappy Bird QA 자동화](./01.game-automation/01.flappy-bird) | PC | ✅ 완료 |

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