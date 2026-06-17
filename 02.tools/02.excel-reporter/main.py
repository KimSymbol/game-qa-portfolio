import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import reporter

# 커맨드라인 인자로 파일명 지정 가능
# 예: python main.py bugs.csv
파일명 = sys.argv[1] if len(sys.argv) > 1 else "bugs.csv"

print("📊 엑셀 리포트 생성 시작...")
print("━" * 30)

# 1. 데이터 읽기
df = reporter.데이터_읽기(파일명)
if df is None:
    exit()

# 2. 통계 출력
print(f"총 버그 수  : {len(df)}건")
print(f"해결        : {len(df[df['상태'] == '해결'])}건 ✅")
print(f"진행중      : {len(df[df['상태'] == '진행중'])}건 🟡")
print(f"미해결      : {len(df[df['상태'] == '미해결'])}건 🔴")
print(f"해결률      : {round(len(df[df['상태'] == '해결']) / len(df) * 100, 1)}%")
print("━" * 30)

# 3. 리포트 생성
저장경로 = reporter.리포트_생성(df)
print(f"✅ 리포트 저장 완료: {저장경로}")