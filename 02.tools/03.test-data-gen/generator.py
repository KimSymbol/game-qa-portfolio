# 역할: QA 테스트에 필요한 더미 데이터를 자동으로 생성하는 모듈
# 생성 가능한 데이터:
#   - 버그 리포트 (CSV)
#   - 게임 로그 (TXT)
#   - 유저 계정 (CSV)
#   - 테스트 케이스 (CSV)
#   - 캐릭터 스탯 (CSV)
#   - 서버 응답 시간 (CSV)

import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

# 한국어 + 영어 faker 동시 사용
fake_ko = Faker("ko_KR")   # 한국어 데이터 (이름, 날짜 등)
fake_en = Faker("en_US")   # 영어 데이터 (이메일, ID 등)

# generator.py 가 있는 폴더를 기준 경로로 설정
기준경로 = Path(__file__).parent

# ── 공통 데이터 풀 ──
심각도목록    = ["Critical", "High", "Medium", "Low"]
우선순위목록  = ["High", "Medium", "Low"]
상태목록      = ["미해결", "진행중", "해결"]
플랫폼목록    = ["PC", "Android", "iOS"]
로그유형목록  = ["ERROR", "WARNING", "INFO"]
직업목록      = ["전사", "마법사", "궁수", "도적", "성직자"]
맵목록        = ["초원", "던전", "설원", "사막", "화산"]

버그제목목록 = [
    "캐릭터가 벽을 통과함",
    "인벤토리 아이템이 사라짐",
    "스킬 시전 시 게임이 멈춤",
    "로그인 후 화면이 검게 변함",
    "몬스터 AI가 동작하지 않음",
    "사운드가 끊기는 현상",
    "서버 응답 없음",
    "UI 텍스트가 겹침",
    "캐릭터 스탯이 잘못 표시됨",
    "퀘스트 완료 후 보상 미지급",
]

에러메시지목록 = [
    "NullReferenceException 발생",
    "IndexOutOfRangeException 발생",
    "Connection timeout",
    "메모리 부족 경고",
    "렌더링 오류 감지",
    "물리 충돌 계산 오류",
    "네트워크 패킷 손실",
]


def 날짜_생성(시작일="2026-01-01", 범위=180):
    """
    시작일로부터 범위 내 랜덤 날짜 생성

    매개변수:
    - 시작일: 기준 날짜 문자열 (YYYY-MM-DD)
    - 범위  : 시작일로부터 최대 며칠 이후까지 (기본 180일)

    반환값:
    - 날짜 문자열 (YYYY-MM-DD)
    """
    기준 = datetime.strptime(시작일, "%Y-%m-%d")
    랜덤날짜 = 기준 + timedelta(days=random.randint(0, 범위))
    return 랜덤날짜.strftime("%Y-%m-%d")


def 결과폴더_생성():
    """결과 폴더가 없으면 자동 생성"""
    폴더 = 기준경로 / "결과"
    폴더.mkdir(exist_ok=True)
    return 폴더


# ────────────────────────────────────────
# ① 버그 리포트 생성 (CSV)
# ────────────────────────────────────────
def 버그리포트_생성(건수=20):
    """
    버그 리포트 더미 데이터를 CSV로 생성

    매개변수:
    - 건수: 생성할 버그 리포트 수 (기본 20건)

    컬럼:
    - 버그ID, 제목, 심각도, 우선순위, 플랫폼, 버전
    - 상태, 발견자, 발견일, 해결일, 재현율

    파일 위치: 결과/bugs_YYYY-MM-DD.csv
    """
    폴더   = 결과폴더_생성()
    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 폴더 / f"bugs_{오늘}.csv"

    헤더 = ["버그ID", "제목", "심각도", "우선순위", "플랫폼",
            "버전", "상태", "발견자", "발견일", "해결일", "재현율"]

    with open(파일명, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(헤더)

        for i in range(1, 건수 + 1):
            발견일 = 날짜_생성()
            상태   = random.choice(상태목록)

            # 해결 상태면 해결일 추가, 아니면 빈 값
            해결일 = 날짜_생성(발견일, 30) if 상태 == "해결" else ""

            # 재현율: 1~10 중 랜덤
            재현횟수 = random.randint(1, 10)
            재현율   = f"{재현횟수}/10"

            writer.writerow([
                f"BUG-{i:03d}",                    # BUG-001 형식
                random.choice(버그제목목록),
                random.choice(심각도목록),
                random.choice(우선순위목록),
                random.choice(플랫폼목록),
                f"v1.{random.randint(0, 9)}.{random.randint(0, 99)}",
                상태,
                fake_ko.name(),                    # 한국어 이름
                발견일,
                해결일,
                재현율,
            ])

    print(f"✅ 버그 리포트 {건수}건 생성 완료: {파일명}")
    return 파일명


# ────────────────────────────────────────
# ② 게임 로그 생성 (TXT)
# ────────────────────────────────────────
def 게임로그_생성(건수=50):
    """
    게임 서버 로그 더미 데이터를 TXT로 생성
    log-analyzer 도구로 바로 분석 가능한 형식으로 생성

    매개변수:
    - 건수: 생성할 로그 줄 수 (기본 50줄)

    형식: [로그유형]: [내용] [버그ID(에러일때만)] at [HH:MM:SS]
    파일 위치: 결과/logs_YYYY-MM-DD.txt
    """
    폴더   = 결과폴더_생성()
    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 폴더 / f"logs_{오늘}.txt"

    에러내용목록 = [
        "캐릭터 충돌 감지",
        "서버 응답 없음",
        "프레임 드랍 발생",
        "메모리 누수 감지",
        "네트워크 패킷 손실",
    ]
    정보내용목록 = [
        "서버 연결 정상",
        "유저 로그인 성공",
        "데이터 로딩 완료",
        "세션 유지 중",
        "캐시 업데이트 완료",
    ]
    경고내용목록 = [
        "메모리 사용량 80%",
        "CPU 사용량 높음",
        "네트워크 지연 감지",
        "디스크 용량 부족",
    ]

    with open(파일명, "w", encoding="utf-8") as f:
        버그번호 = 1
        for _ in range(건수):
            유형 = random.choice(로그유형목록)

            # 랜덤 시간 생성 (HH:MM:SS)
            시간 = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

            if 유형 == "ERROR":
                내용   = random.choice(에러내용목록)
                버그ID = f"BUG-{버그번호:03d}"
                버그번호 += 1
                f.write(f"ERROR: {내용} {버그ID} at {시간}\n")
            elif 유형 == "WARNING":
                내용 = random.choice(경고내용목록)
                f.write(f"WARNING: {내용} at {시간}\n")
            else:
                내용 = random.choice(정보내용목록)
                f.write(f"INFO: {내용}\n")

    print(f"✅ 게임 로그 {건수}줄 생성 완료: {파일명}")
    return 파일명


# ────────────────────────────────────────
# ③ 유저 계정 생성 (CSV)
# ────────────────────────────────────────
def 유저계정_생성(건수=30):
    """
    게임 유저 계정 더미 데이터를 CSV로 생성

    매개변수:
    - 건수: 생성할 유저 수 (기본 30명)

    컬럼:
    - 유저ID, 닉네임, 이메일, 가입일, 최종접속일
    - 레벨, 플랫폼, 국가, 계정상태

    파일 위치: 결과/users_YYYY-MM-DD.csv
    """
    폴더   = 결과폴더_생성()
    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 폴더 / f"users_{오늘}.csv"

    계정상태목록 = ["정상", "정지", "탈퇴"]

    헤더 = ["유저ID", "닉네임", "이메일", "가입일",
            "최종접속일", "레벨", "플랫폼", "국가", "계정상태"]

    with open(파일명, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(헤더)

        for i in range(1, 건수 + 1):
            가입일     = 날짜_생성("2025-01-01", 365)
            최종접속일 = 날짜_생성(가입일, 30)

            writer.writerow([
                f"USR-{i:04d}",
                fake_ko.user_name(),              # 한국어 닉네임
                fake_en.email(),                  # 영어 이메일
                가입일,
                최종접속일,
                random.randint(1, 100),           # 레벨 1~100
                random.choice(플랫폼목록),
                random.choice(["KR", "US", "JP", "CN"]),
                random.choice(계정상태목록),
            ])

    print(f"✅ 유저 계정 {건수}건 생성 완료: {파일명}")
    return 파일명


# ────────────────────────────────────────
# ④ 테스트 케이스 생성 (CSV)
# ────────────────────────────────────────
def 테스트케이스_생성(건수=20):
    """
    QA 테스트 케이스 더미 데이터를 CSV로 생성
    md-report-gen 도구의 입력 파일로 바로 사용 가능

    매개변수:
    - 건수: 생성할 테스트 케이스 수 (기본 20건)

    컬럼:
    - TC_ID, 테스트명, 분류, 전제조건
    - 테스트단계, 예상결과, 실제결과, 결과
    - 심각도, 우선순위, 플랫폼, 발견자, 발견일

    파일 위치: 결과/testcases_YYYY-MM-DD.csv
    """
    폴더   = 결과폴더_생성()
    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 폴더 / f"testcases_{오늘}.csv"

    분류목록 = ["로그인", "회원가입", "인벤토리", "전투", "퀘스트", "상점", "설정"]
    결과목록 = ["Pass", "Fail", "Block", "Skip"]

    테스트명목록 = [
        "정상 로그인 확인",
        "잘못된 비밀번호 입력 시 오류 메시지 확인",
        "아이템 구매 후 인벤토리 반영 확인",
        "몬스터 처치 시 경험치 획득 확인",
        "퀘스트 수락 후 목표 표시 확인",
        "캐릭터 이동 정상 동작 확인",
        "스킬 사용 시 마나 소모 확인",
        "게임 종료 후 재실행 시 저장 데이터 불러오기 확인",
    ]

    전제조건목록 = [
        "게임이 실행된 상태",
        "로그인된 상태",
        "캐릭터 생성 완료 상태",
        "인벤토리에 아이템이 있는 상태",
    ]

    헤더 = ["TC_ID", "테스트명", "분류", "전제조건",
            "테스트단계", "예상결과", "실제결과", "결과",
            "심각도", "우선순위", "플랫폼", "발견자", "발견일"]

    with open(파일명, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(헤더)

        for i in range(1, 건수 + 1):
            결과 = random.choice(결과목록)

            # Pass면 실제결과 = 예상결과와 같음
            # Fail이면 실제결과 = 오류 내용
            예상결과 = "정상 동작 확인"
            실제결과 = "정상 동작 확인" if 결과 == "Pass" else random.choice(에러메시지목록)

            writer.writerow([
                f"TC-{i:03d}",
                random.choice(테스트명목록),
                random.choice(분류목록),
                random.choice(전제조건목록),
                "1. 앱 실행\n2. 해당 기능 진입\n3. 동작 수행",
                예상결과,
                실제결과,
                결과,
                random.choice(심각도목록) if 결과 == "Fail" else "",
                random.choice(우선순위목록) if 결과 == "Fail" else "",
                random.choice(플랫폼목록),
                fake_ko.name(),
                날짜_생성(),
            ])

    print(f"✅ 테스트 케이스 {건수}건 생성 완료: {파일명}")
    return 파일명


# ────────────────────────────────────────
# ⑤ 캐릭터 스탯 생성 (CSV)
# ────────────────────────────────────────
def 캐릭터스탯_생성(건수=30):
    """
    게임 캐릭터 스탯 더미 데이터를 CSV로 생성
    캐릭터 밸런스 테스트나 데이터 검증 테스트에 활용

    매개변수:
    - 건수: 생성할 캐릭터 수 (기본 30명)

    컬럼:
    - 캐릭터ID, 닉네임, 직업, 레벨, HP, MP
    - 공격력, 방어력, 속도, 현재맵, 플레이타임(시간)

    파일 위치: 결과/characters_YYYY-MM-DD.csv
    """
    폴더   = 결과폴더_생성()
    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 폴더 / f"characters_{오늘}.csv"

    # 직업별 스탯 범위 정의
    # (HP범위, MP범위, 공격력범위, 방어력범위, 속도범위)
    직업스탯 = {
        "전사" : ((800, 1200), (100, 300),  (80, 150),  (100, 180), (50, 80)),
        "마법사": ((400, 700),  (500, 1000), (150, 250), (30, 70),   (60, 90)),
        "궁수" : ((500, 800),  (200, 400),  (100, 180), (50, 100),  (90, 130)),
        "도적" : ((450, 750),  (150, 350),  (120, 200), (40, 80),   (110, 150)),
        "성직자": ((600, 900),  (400, 800),  (50, 100),  (70, 120),  (55, 85)),
    }

    헤더 = ["캐릭터ID", "닉네임", "직업", "레벨",
            "HP", "MP", "공격력", "방어력", "속도",
            "현재맵", "플레이타임(시간)"]

    with open(파일명, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(헤더)

        for i in range(1, 건수 + 1):
            직업  = random.choice(직업목록)
            레벨  = random.randint(1, 100)
            스탯  = 직업스탯[직업]

            # 레벨에 따라 스탯 배율 적용
            배율 = 1 + (레벨 / 100)

            writer.writerow([
                f"CHR-{i:04d}",
                fake_ko.user_name(),
                직업,
                레벨,
                int(random.randint(*스탯[0]) * 배율),  # HP
                int(random.randint(*스탯[1]) * 배율),  # MP
                int(random.randint(*스탯[2]) * 배율),  # 공격력
                int(random.randint(*스탯[3]) * 배율),  # 방어력
                int(random.randint(*스탯[4]) * 배율),  # 속도
                random.choice(맵목록),
                random.randint(1, 500),                # 플레이타임
            ])

    print(f"✅ 캐릭터 스탯 {건수}건 생성 완료: {파일명}")
    return 파일명


# ────────────────────────────────────────
# ⑥ 서버 응답 시간 생성 (CSV)
# ────────────────────────────────────────
def 서버응답_생성(건수=100):
    """
    게임 서버 응답 시간 더미 데이터를 CSV로 생성
    성능 테스트 결과 분석이나 임계값 검증에 활용

    매개변수:
    - 건수: 생성할 응답 기록 수 (기본 100건)

    컬럼:
    - 요청ID, API명, 요청시간, 응답시간(ms), 상태코드
    - 성공여부, 서버, 지역

    임계값 기준:
    - 정상  : 응답시간 200ms 미만
    - 경고  : 응답시간 200~500ms
    - 위험  : 응답시간 500ms 이상

    파일 위치: 결과/server_response_YYYY-MM-DD.csv
    """
    폴더   = 결과폴더_생성()
    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 폴더 / f"server_response_{오늘}.csv"

    API목록 = [
        "/api/login",
        "/api/logout",
        "/api/character/stats",
        "/api/inventory/list",
        "/api/quest/accept",
        "/api/shop/purchase",
        "/api/battle/start",
        "/api/ranking/top100",
    ]

    상태코드목록 = [200, 200, 200, 200, 201, 400, 404, 500]  # 200이 더 자주
    서버목록     = ["서버-KR-01", "서버-KR-02", "서버-US-01"]
    지역목록     = ["서울", "부산", "뉴욕"]

    헤더 = ["요청ID", "API명", "요청시간", "응답시간(ms)",
            "상태코드", "성공여부", "서버", "지역"]

    with open(파일명, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(헤더)

        for i in range(1, 건수 + 1):
            응답시간   = random.randint(50, 800)   # 50~800ms
            상태코드   = random.choice(상태코드목록)
            성공여부   = "성공" if 상태코드 < 400 else "실패"

            # 요청 시간 (오늘 날짜 기준 랜덤 시간)
            요청시간 = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

            writer.writerow([
                f"REQ-{i:05d}",
                random.choice(API목록),
                요청시간,
                응답시간,
                상태코드,
                성공여부,
                random.choice(서버목록),
                random.choice(지역목록),
            ])

    print(f"✅ 서버 응답 기록 {건수}건 생성 완료: {파일명}")
    return 파일명