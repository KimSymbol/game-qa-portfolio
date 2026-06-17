# 역할: 로그 분석을 자동으로 주기적으로 실행하는 스케줄러
# 매일 지정 시간에 main.py 를 자동 실행
#
# 실행 방법:
#   python scheduler.py        → 스케줄러 시작 (Ctrl+C 로 종료)

import schedule    # 스케줄링 라이브러리
import time        # 대기 시간 처리
import subprocess  # 외부 프로세스 실행
from pathlib import Path

# scheduler.py 가 있는 폴더를 기준 경로로 설정
기준경로 = Path(__file__).parent


def 분석_실행():
    """
    main.py 를 subprocess 로 실행
    스케줄러가 지정 시간마다 이 함수를 호출
    """
    print("⏰ 자동 분석 시작...")
    subprocess.run(["python", str(기준경로 / "main.py")])


# ── 스케줄 설정 ──
# 매일 오전 9시에 자동 실행
schedule.every().day.at("09:00").do(분석_실행)

# 1시간마다 실행하고 싶으면 아래 주석 해제
# schedule.every(1).hours.do(분석_실행)

# 테스트용: 1분마다 실행하고 싶으면 아래 주석 해제
# schedule.every(1).minutes.do(분석_실행)

print("✅ 스케줄러 시작 (Ctrl+C 로 종료)")
print(f"⏰ 매일 09:00 에 자동 분석 실행")
print("━" * 30)

# ── 스케줄러 실행 루프 ──
# 60초마다 예약된 작업이 있는지 확인
while True:
    schedule.run_pending()   # 예약된 작업 실행
    time.sleep(60)           # 60초 대기