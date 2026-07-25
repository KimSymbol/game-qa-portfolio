# 🎮 Game QA Automation Portfolio

게임 QA 자동화 포트폴리오입니다.
PC 게임 및 모바일 게임을 대상으로 자동화 테스트를 구현하고,
QA 업무 전반을 자동화하는 실무 도구를 개발했습니다.

## 📁 프로젝트 구조

```
game-qa-portfolio/
├── .github/workflows...  # 깃허브 액션 CI/CD 설정
├── 01.game-automation/
│    ├── 01.flappy-bird/  # Flappy Bird QA 자동화
│    ├── 02.flare-rpg/    # Flare RPG QA 자동화
│    └── 03.2048-mobile/  # 2048 Mobile QA 자동화
├── 02.tools/             # QA 도구 모음 (6개 도구 + 파이프라인)
│    ├── 01.test-data-gen/     # 더미 데이터 생성 (9종)
│    ├── 02.data-validator/    # 데이터 무결성 검증 (8종 검사)
│    ├── 03.md-report-gen/     # 마크다운 버그 리포트
│    ├── 04.excel-reporter/    # 통합 리포트 (xlsx/json/html/pdf)
│    ├── 05.log-analyzer/      # 로그 분석 + 버그 이력 추적
│    ├── 06.tc-generator/      # TC 자동 생성
│    ├── common/               # 공통 모듈 (입출력/스타일/로깅/매핑)
│    └── pipeline.py           # 통합 자동화 스크립트
├── 03.추가 예정          # 분석서, 테스트케이스 등(추가 예정)
└── .gitmodules           # 서브 모듈 (FlapPybird)
```

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| **언어** | Python 3.12 |
| **게임 자동화** | PyAutoGUI · pydirectinput · OpenCV · pywin32 |
| **모바일 자동화** | uiautomator2 · ADB |
| **기기 미러링** | scrcpy |
| **테스트** | pytest · Allure |
| **데이터 처리** | pandas · openpyxl · csv · json |
| **리포트 생성** | openpyxl · reportlab (PDF) · HTML |
| **더미 데이터** | Faker (ko_KR · en_US) |
| **CI/CD** | GitHub Actions (self-hosted runner) |
| **외부 연동** | Jira REST API v3 · Slack Webhook |
| **리포트 배포** | Allure Report (GitHub Pages 자동 배포) |
| **로깅** | logging (파일 + 콘솔 동시 출력) |

## 🧰 사용 도구

| 분류 | 도구 |
|------|------|
| **AI 보조** | Claude |
| **IDE** | VS Code · Cursor |
| **터미널** | Warp · PowerShell |
| **버그 트래킹** | Jira |
| **알림/협업** | Slack |

## 📊 프로젝트 목록

### 🎮 01. Game Automation

| # | 프로젝트 | 기술 스택 | 상태 |
|---|---------|----------|------|
| 01 | [Flappy Bird QA 자동화](./01.game-automation/01.flappy-bird) | PyAutoGUI · OpenCV · pytest · Allure | ✅ 완료 |
| 02 | [Flare RPG QA 자동화](./01.game-automation/02.flare-rpg) | PyAutoGUI · OpenCV · pytest · Allure | ✅ 완료 |
| 03 | [2048 Mobile QA 자동화](./01.game-automation/03.2048-mobile) | uiautomator2 · ADB · pytest · Allure | ✅ 완료 |

### 🛠️ 02. Tools ([상세 문서](./02.tools/README.md))

| # | 도구 | 역할 | 입력 | 출력 |
|---|------|------|------|------|
| 01 | [test-data-gen](./02.tools/01.test-data-gen) | 더미 데이터 생성 (9종) | - | csv, txt |
| 02 | [data-validator](./02.tools/02.data-validator) | 데이터 무결성 검증 (8종 검사) | csv, xlsx | xlsx, json, html |
| 03 | [md-report-gen](./02.tools/03.md-report-gen) | 마크다운 버그 리포트 | csv, xlsx | md, csv |
| 04 | [excel-reporter](./02.tools/04.excel-reporter) | 통합 리포트 생성 | csv, xlsx, tsv, json | xlsx, json, html, pdf |
| 05 | [log-analyzer](./02.tools/05.log-analyzer) | 로그 분석 + 버그 이력 추적 | txt, log | xlsx, json, html |
| 06 | [tc-generator](./02.tools/06.tc-generator) | TC 자동 생성 | json | csv, xlsx |
| - | [common](./02.tools/common) | 공통 모듈 + 외부 데이터 변환 | - | - |
| - | [pipeline.py](./02.tools/pipeline.py) | 6개 도구 통합 자동 실행 | - | - |

**빠른 실행:**
```bash
cd 02.tools
pip install -r requirements.txt
python pipeline.py --all --open
```

## 🔗 Allure 리포트

게임별 최신 자동화 테스트 리포트입니다.

| 게임 | Allure 리포트 |
|------|---------------|
| 🐦 Flappy Bird | [리포트 보기](https://kimsymbol.github.io/game-qa-portfolio/flappy-bird/) |
| 🗡️ Flare RPG | [리포트 보기](https://kimsymbol.github.io/game-qa-portfolio/flare-rpg/) |
| 📱 2048 Mobile | [보기](https://kimsymbol.github.io/game-qa-portfolio/2048-mobile/) |

## 🎬 시연 영상

👉 [Flappy Bird QA 자동화 테스트](https://youtu.be/gc4bCL45jqw)

👉 [Flare RPG QA 자동화 시연](https://youtu.be/SkB1OpMsIvU)

👉 [2048 Mobile QA 자동화 시연](https://youtu.be/1gs1ShVXCl8)

👉 [QA Tool 전체 시연](https://youtu.be/J9GxlsjLduU)

## 📋 팀 프로젝트 경험

### AI 헬피챗 QA 자동화 (부트캠프 팀 프로젝트)

| 항목 | 내용 |
|------|------|
| **대상 서비스** | AI 헬피챗 웹 서비스 |
| **기술 스택** | Selenium · pytest · GitLab CI/CD · Allure · Jira API |
| **주요 구현** | 회원가입(SI) · 로그인(LI) · 수업지도안(TS) 플로우 UI 자동화 |
| **특이사항** | Jira REST API v3 연동으로 버그 티켓 자동 생성 및 중복 방지 처리, 실 서비스 품질 향상에 영향을 줌 |