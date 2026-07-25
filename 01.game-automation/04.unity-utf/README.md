# 🎮 Unity QA 자동화 (Unity Test Framework)

Sentry에서 개발한 오픈소스 Unity 게임 [Sentaur Survivors](https://github.com/sentry-demos/unity)를 대상으로
Unity Test Framework 기반 PlayMode 자동화 테스트를 구현했습니다.

앞선 세 프로젝트가 **화면을 통해 외부에서 검증**했다면,
이 프로젝트는 **게임 엔진 내부의 GameObject와 필드에 직접 접근**하여 검증합니다.

## 🎬 시연 영상

👉 추후 업데이트 예정

## 🛠️ 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| **게임 엔진** | Unity 6.3 LTS (6000.3.8f1) | 테스트 대상 |
| **테스트 프레임워크** | Unity Test Framework (NUnit) | PlayMode 테스트 작성 및 실행 |
| **테스트 언어** | C# | 게임 코드와 동일 언어로 타입 안전 접근 |
| **실행 제어** | Python 3.12 | Unity CLI 실행, NUnit XML 파싱 |
| **CI/CD** | GitHub Actions | self-hosted runner에서 batchmode 실행 |
| **버그 트래킹** | Jira REST API v3 | 실패 시 티켓 생성 + 중복 시 댓글 |
| **알림** | Slack Webhook (Block Kit) | 결과 요약 |
| **버그 리포트** | CSV/XLSX (openpyxl) | 02.tools 컬럼 구조 호환 |
| **리포트** | Allure | NUnit 결과를 Allure 포맷으로 변환하여 배포 |

## 🔍 도구 선정 과정

당초 **AltTester Unity SDK**를 우선 검토했습니다.
Python으로 테스트를 작성할 수 있고 앞선 프로젝트와 언어를 통일할 수 있다는 장점 때문이었습니다.

실제로 SDK 계측까지 완료했으나, 다음 제약으로 채택하지 않았습니다.

| 항목 | 제약 |
|------|------|
| CLI 배치 모드 | Pro 라이선스 필요 → **CI 자동화 불가** |
| Pro 무료 체험 | 회사 이메일만 가입 허용 |
| 무료 티어 | 서버 GUI 수동 실행만 가능 |

앞선 세 프로젝트가 모두 CI 자동화를 핵심으로 삼았기에,
**CI 실행이 불가능한 도구는 이 포트폴리오에서 채택할 수 없다**고 판단했습니다.

Unity Test Framework는 완전 무료이며 `-runTests` CLI 옵션으로 배치 실행이 가능합니다.
언어는 C#으로 바뀌지만, 오히려 게임 코드와 동일 언어라 타입 안전한 접근이 가능해졌습니다.

> 도구는 기능만이 아니라 **라이선스와 운영 제약까지 검토한 뒤 선정해야 한다**는 것을 확인한 과정이었습니다.

## 🧪 테스트 설계

### 접근 방식 — 화이트박스 테스트

Unity 게임은 화면 전체가 하나의 `SurfaceView`로 렌더링되므로,
uiautomator2 같은 UI 속성 기반 도구로는 내부 요소에 접근할 수 없습니다.

Unity Test Framework는 게임과 **동일한 프로세스 내부에서 실행**되므로
GameObject와 컴포넌트 필드에 직접 접근합니다.

```csharp
// 문자열이 아닌 타입으로 접근 → 오타는 컴파일 단계에서 검출
var weaponManager = Object.FindFirstObjectByType<WeaponManager>();
weaponManager.UpgradeDamage(1);

Assert.AreEqual(1.3f, weaponManager.GlobalDamageModifier, 0.001f);
```

`GlobalDamageModifier`가 1.3인지 1.35인지는 **화면 어디에도 표시되지 않습니다.**
이미지 기반 자동화로는 검증이 불가능한 영역입니다.

### 접근성에 따른 검증 전략

게임 코드의 접근 제한자에 따라 검증 방식을 달리 적용했습니다.

| 대상 | 접근성 | 검증 방식 |
|------|--------|----------|
| `Enemy.hitpoints` | public | 필드 직접 비교 |
| `WeaponManager.GlobalDamageModifier` | public | 필드 직접 비교 |
| `Player._hitPoints` | private | 체력바 `Slider.value`로 간접 검증 |

private 필드는 Reflection으로 강제 접근할 수 있으나 사용하지 않았습니다.
테스트가 내부 구현에 결합되면 리팩터링 시 대량으로 깨지기 때문입니다.
대신 **사용자가 실제로 보는 지표**인 체력바 값으로 검증했습니다.

### 테스트 케이스

| ID | 분류 | 테스트명 | 절차 | 기대 결과 | 검증 방식 |
|----|------|---------|------|----------|----------|
| UT-001 | 씬 | 타이틀 씬 로드 | TitleScene 로드 | 활성 씬 전환 | 씬 상태 |
| UT-002 | 씬 | 배틀 씬 플레이어 존재 | BattleScene 로드 | Player 오브젝트 존재 | 타입 탐색 |
| UT-003 | 전투 | 적 피격 시 체력 감소 | 적에게 5 데미지 | hitpoints 정확히 5 감소 | public 필드 |
| UT-004 | 전투 | 적 체력 음수 방지 | 9999 데미지 적용 | hitpoints 0으로 고정 | 경계값 |
| UT-005 | 전투 | 적 사망 시 오브젝트 제거 | 치명타 후 애니메이션 대기 | GameObject 파괴 | 오브젝트 상태 |
| UT-006 | 무기 | 데미지 업그레이드 배율 | UpgradeDamage(1/2/3) | 1.3 / 1.6 / 2.0 | public 필드 |
| UT-007 | 무기 | 쿨다운 업그레이드 배율 | UpgradeCooldown(1/3) | 0.8 / 0.3 | public 필드 |
| UT-008 | 무기 | 정의되지 않은 레벨 입력 | UpgradeDamage(99) | 배율 미변경 | 경계값 |
| UT-009 | 플레이어 | 피격 시 체력바 감소 | 30 데미지 적용 | 체력바 0.7 표시 | Slider 간접 |
| UT-010 | 플레이어 | 회복 시 최대치 초과 방지 | 50 피해 후 100 회복 | 체력바 1.0 고정 | 경계값 |
| UT-011 | 플레이어 | 데미지 저항 적용 | 저항 50% 후 30 데미지 | 실제 피해 15 | 상대 비교 |

케이스 11개, 실행 메서드 14개 (UT-006/007은 레벨별로 분리).

### 테스트 설계 핵심 원칙

- **완전한 독립성**: 각 테스트가 씬을 새로 로드하여 실행 순서와 무관하게 동일한 결과 보장
- **3단 구조**: 변수 선언부 / 함수 선언부 / 메인 실행부로 구분하여 테스트 메서드 본문은 헬퍼 호출 1~3줄로 유지
- **경계값 검증**: 정상 케이스뿐 아니라 음수·초과·미정의 입력까지 포함
- **역할 분리**: C#은 테스트 실행, Python은 실행 제어와 리포팅 담당

### 앞선 프로젝트와의 비교

| 항목 | Flare RPG (PC) | 2048 (Mobile) | Unity (본 프로젝트) |
|------|---------------|--------------|-------------------|
| 접근 방식 | 이미지 매칭 | UI 속성 | **엔진 내부 직접** |
| 테스트 성격 | 블랙박스 | 블랙박스 | **화이트박스** |
| 요소 식별 | 템플릿 이미지 | resource-id 문자열 | **C# 타입** |
| 검증 가능 범위 | 화면에 보이는 것 | 화면에 보이는 것 | **내부 상태 전체** |
| 오타 검출 시점 | 런타임 실패 | 런타임 실패 | **컴파일 단계** |
| 실행 시간 | 약 2분 | 약 20초 | 약 25초 |

## 📁 프로젝트 구조
```
04.unity-utf/
├── runner/
│ └── run_tests.py # 파이프라인 진입점
├── utils/
│ ├── unity_runner.py # Unity CLI 실행 + NUnit XML 파싱
│ ├── jira_reporter.py # Jira 티켓 자동 생성 + 댓글
│ ├── bug_reporter.py # CSV/XLSX 버그 리포트
│ ├── slack_notifier.py # Slack Block Kit 알림
│ └── allure_reporter.py # NUnit → Allure 포맷 변환
├── tests-source/ # 게임에 주입할 C# 테스트 원본
│ ├── Tests/
│ │ ├── SceneLoadTest.cs # UT-001 ~ UT-002
│ │ ├── EnemyCombatTest.cs # UT-003 ~ UT-005
│ │ ├── WeaponUpgradeTest.cs # UT-006 ~ UT-008
│ │ ├── PlayerStatusTest.cs # UT-009 ~ UT-011
│ │ └── Tests.asmdef # 테스트 어셈블리 정의
│ └── Scripts/
│ └── SentaurSurvivors.asmdef # 게임 코드 어셈블리 정의
├── .env # Unity 경로, Jira/Slack 설정 (.gitignore)
└── requirements.txt
```

### 테스트 코드 주입 구조

테스트 대상 게임은 **submodule로 원본 저장소를 참조**하며 재배포하지 않습니다.
따라서 원본에 없는 테스트 코드와 어셈블리 정의는 실행 시점에 주입합니다.
```
1. submodule 체크아웃 (원본 게임)
2. tests-source/Scripts/*.asmdef → Assets/Scripts/
3. tests-source/Tests/* → Assets/Tests/
4. Unity CLI batchmode 실행
```

## 🔧 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 테스트에서 게임 클래스를 참조할 수 없음 | asmdef로 정의된 어셈블리는 기본 어셈블리(Assembly-CSharp)를 참조 불가 | 게임 코드에도 asmdef를 추가하고 테스트 어셈블리가 이를 참조하도록 구성 |
| TMPro 타입 미발견 컴파일 오류 | asmdef 추가로 TextMeshPro 참조가 끊김 | asmdef에 `Unity.TextMeshPro` 참조 추가 |
| Windows 빌드 실패 | 프로젝트가 IL2CPP 설정인데 해당 모듈 미설치 | PC 검증용이므로 Scripting Backend를 Mono로 변경 |
| **로컬 통과, CI에서 13개 실패** | batchmode에는 입력 장치가 없어 `OnScreenControl`이 `InvalidOperationException` 발생. UTF는 예외를 자동으로 실패 처리 | 씬 로드 헬퍼에 `LogAssert.ignoreFailingMessages` 적용 |
| Unity Hub에서 프로젝트 인식 실패 | Hub와 Editor가 서로 다른 드라이브에 설치됨 | Editor를 CLI로 직접 실행하여 우회 후 Hub 설정 경로 수정 |
| 스크린샷 첨부 불가 | batchmode는 화면 렌더링 없음 | NUnit이 제공하는 stack trace로 대체 (파일 경로·라인 번호 포함으로 오히려 재현성 향상) |

### CI 환경 검증의 필요성

이 프로젝트에서도 **로컬에서 전체 통과하던 테스트가 CI에서 대량 실패**했습니다.
2048 프로젝트에서 동일한 패턴을 겪은 뒤였습니다.

| 프로젝트 | 로컬 | CI | 원인 |
|---------|------|-----|------|
| 2048 | 통과 | TW-003 실패 | 랜덤 초기 배치로 단일 방향 스와이프가 무효 |
| Unity | 통과 | 13개 실패 | batchmode 입력 장치 부재 |

두 사례 모두 테스트 로직이 아니라 **실행 환경 차이**가 원인이었습니다.
로컬 통과만으로 자동화가 완성됐다고 볼 수 없다는 점을 확인했습니다.

## 🔬 코드 리뷰로 발견한 잠재 결함

자동화 테스트는 **현재 설정값에서의 동작**만 검증합니다.
설정이 바뀌었을 때 드러날 결함은 코드 리뷰에서 발견했습니다.

### Player.ApplyHeal — 최대 체력 하드코딩

```csharp
public void ApplyHeal(int healAmount = 0)
{
    _hitPoints += healAmount;
    _hitPoints = Math.Min(_hitPoints, 100);  // ← _maxHitPoints 여야 함
    _healthBar.SetHealth(1.0f * _hitPoints / _maxHitPoints);
}
```

같은 클래스의 `ApplyDamage`는 `_maxHitPoints`를 사용하는 반면 이 메서드만 `100`을 하드코딩했습니다.
현재는 `_maxHitPoints`가 100이라 문제가 없으나,
밸런싱으로 최대 체력을 150으로 조정하면 회복 상한이 100에서 멈춰 체력바가 67%를 넘지 못합니다.

### WeaponManager.Upgrade — 정의 범위 밖 입력 무시

```csharp
if (level == 1) { ... } else if (level == 2) { ... } else if (level == 3) { ... }
// level이 0 또는 4 이상이면 아무 동작 없이 종료
```

에러도 로그도 없이 조용히 무시되므로 발견이 어려운 유형입니다.
UT-008에서 이 동작을 명시적으로 문서화하여, 향후 동작이 변경되면 테스트가 감지하도록 했습니다.

> 자동화 테스트와 코드 리뷰는 서로 다른 종류의 결함을 발견하는 **상호 보완적 활동**입니다.

## ⚙️ 실행 방법

### 사전 준비

```bash
# 게임 프로젝트 submodule 초기화
git submodule update --init --recursive

# Unity Editor 6000.3.8f1 설치 (Unity Hub)
# Android Build Support 모듈 포함 권장
```

### 로컬 실행

```bash
# venv 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# .env 설정
# UNITY_EDITOR_PATH=...\Unity.exe
# UNITY_PROJECT_PATH=...\sentaur-survivors

# 전체 파이프라인 실행 (테스트 → Jira/Slack/버그리포트 → Allure)
python runner/run_tests.py

# Allure 리포트 확인
allure serve allure-results
```

### Unity Editor에서 실행

개발 중에는 Editor의 Test Runner에서 직접 실행할 수 있습니다.