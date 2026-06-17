import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import qa_tools

print("🔍 로그 파일 분석 시작...")
print("━" * 25)

# 1. 로그 읽기
전체로그 = qa_tools.로그_읽기("bug_log.txt")

# 2. 에러 필터링
에러로그 = qa_tools.에러_필터링(전체로그)

# 3. 버그 정보 추출
버그목록 = [qa_tools.버그정보_추출(로그) for 로그 in 에러로그]

# 4. 통계 출력
error수   = sum(1 for 로그 in 전체로그 if "ERROR"   in 로그)
warning수 = sum(1 for 로그 in 전체로그 if "WARNING" in 로그)
info수    = sum(1 for 로그 in 전체로그 if "INFO"    in 로그)
버그ID목록 = [버그["버그ID"] for 버그 in 버그목록]

print(f"총 로그 수    : {len(전체로그)}건")
print(f"ERROR         : {error수}건 🔴")
print(f"WARNING       : {warning수}건 🟡")
print(f"INFO          : {info수}건 🟢")
print(f"버그 ID 목록  : {버그ID목록}")
print("━" * 25)

# 5. 엑셀 저장 ← 전체로그 추가!
저장경로 = qa_tools.엑셀_저장(버그목록, 전체로그)
print(f"✅ 결과 저장 완료: {저장경로}")