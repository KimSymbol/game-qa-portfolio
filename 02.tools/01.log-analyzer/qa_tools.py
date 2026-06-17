import re
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from datetime import datetime

# 기준 경로
기준경로 = Path(__file__).parent


# ① 로그 파일 읽기
def 로그_읽기(파일명):
    경로 = 기준경로 / 파일명
    if not 경로.exists():
        print("❌ 파일이 없어요:", 경로)
        return []
    with open(경로, "r", encoding="utf-8") as f:
        return f.readlines()


# ② 에러 로그만 필터링
def 에러_필터링(로그목록):
    에러목록 = []
    for 로그 in 로그목록:
        로그 = 로그.strip()
        if "ERROR" in 로그:
            에러목록.append(로그)
    return 에러목록


# ③ 버그 ID / 시간 추출
def 버그정보_추출(로그):
    버그ID = re.search(r"BUG-\d+", 로그)
    시간   = re.search(r"\d{2}:\d{2}:\d{2}", 로그)
    return {
        "로그"  : 로그,
        "버그ID": 버그ID.group() if 버그ID else "없음",
        "시간"  : 시간.group()   if 시간   else "없음"
    }


# ④ 열 너비 자동 조정
def 열너비_조정(ws):
    for 열 in ws.columns:
        최대길이 = 0
        열이름 = 열[0].column_letter

        for 셀 in 열:
            if 셀.value:
                최대길이 = max(최대길이, len(str(셀.value)))

        ws.column_dimensions[열이름].width = 최대길이 + 4


# ⑤ 엑셀 저장
def 엑셀_저장(버그목록, 전체로그):
    결과폴더 = 기준경로 / "결과"
    결과폴더.mkdir(exist_ok=True)

    오늘 = datetime.now().strftime("%Y-%m-%d")
    파일명 = 결과폴더 / f"bug_report_{오늘}.xlsx"

    wb = Workbook()

    # ── 시트 1: 전체 로그 ──
    ws1 = wb.active
    ws1.title = "전체 로그"
    ws1.append(["로그 유형", "내용"])

    for 셀 in ws1[1]:
        셀.fill      = PatternFill("solid", fgColor="4472C4")
        셀.font      = Font(color="FFFFFF", bold=True)
        셀.alignment = Alignment(horizontal="center")

    색상맵 = {
        "ERROR":   "FF0000",
        "WARNING": "FFC000",
        "INFO":    "70AD47",
    }

    for 로그 in 전체로그:
        로그 = 로그.strip()
        유형 = "INFO"
        if "ERROR" in 로그:
            유형 = "ERROR"
        elif "WARNING" in 로그:
            유형 = "WARNING"

        ws1.append([유형, 로그])
        현재행 = ws1.max_row
        for 셀 in ws1[현재행]:
            셀.fill = PatternFill("solid", fgColor=색상맵[유형])

    # ── 시트 2: 버그 리포트 ──
    ws2 = wb.create_sheet(title="버그 리포트")
    ws2.append(["버그ID", "시간", "로그 내용"])

    for 셀 in ws2[1]:
        셀.fill      = PatternFill("solid", fgColor="4472C4")
        셀.font      = Font(color="FFFFFF", bold=True)
        셀.alignment = Alignment(horizontal="center")

    for 버그 in 버그목록:
        ws2.append([버그["버그ID"], 버그["시간"], 버그["로그"]])
        현재행 = ws2.max_row
        for 셀 in ws2[현재행]:
            셀.fill = PatternFill("solid", fgColor="FF0000")
            셀.font = Font(color="FFFFFF")

    # ── 시트 3: 통계 요약 ──
    ws3 = wb.create_sheet(title="통계 요약")
    ws3.append(["항목", "건수"])

    for 셀 in ws3[1]:
        셀.fill      = PatternFill("solid", fgColor="4472C4")
        셀.font      = Font(color="FFFFFF", bold=True)
        셀.alignment = Alignment(horizontal="center")

    통계데이터 = [
        ("ERROR",   sum(1 for 로그 in 전체로그 if "ERROR"   in 로그), "FF0000"),
        ("WARNING", sum(1 for 로그 in 전체로그 if "WARNING" in 로그), "FFC000"),
        ("INFO",    sum(1 for 로그 in 전체로그 if "INFO"    in 로그), "70AD47"),
        ("전체",    len(전체로그),                                     "4472C4"),
    ]

    for 항목, 건수, 색상 in 통계데이터:
        ws3.append([항목, 건수])
        현재행 = ws3.max_row
        for 셀 in ws3[현재행]:
            셀.fill      = PatternFill("solid", fgColor=색상)
            셀.font      = Font(color="FFFFFF", bold=True)
            셀.alignment = Alignment(horizontal="center")

    # 열 너비 자동 조정
    열너비_조정(ws1)
    열너비_조정(ws2)
    열너비_조정(ws3)

    wb.save(파일명)
    return 파일명