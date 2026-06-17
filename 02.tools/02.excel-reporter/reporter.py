import pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter
from datetime import datetime

기준경로 = Path(__file__).parent

# 색상 정의
색상 = {
    "Critical": "FF0000",
    "Major"   : "FFC000",
    "Minor"   : "70AD47",
    "해결"    : "70AD47",
    "진행중"  : "FFC000",
    "미해결"  : "FF0000",
    "헤더"    : "4472C4",
}


# ① CSV 읽기
def 데이터_읽기(파일명):
    경로 = 기준경로 / 파일명
    if not 경로.exists():
        print("❌ 파일이 없어요:", 경로)
        return None
    df = pd.read_csv(경로, encoding="utf-8")
    print(f"✅ 데이터 로딩 완료: {len(df)}건")
    return df


# ② 헤더 스타일 적용
def 헤더_스타일(ws, 행번호=1):
    for 셀 in ws[행번호]:
        셀.fill      = PatternFill("solid", fgColor=색상["헤더"])
        셀.font      = Font(color="FFFFFF", bold=True)
        셀.alignment = Alignment(horizontal="center")


# ③ 열 너비 자동 조정
def 열너비_조정(ws):
    for i, 열 in enumerate(ws.columns, 1):
        최대길이 = 0
        열이름 = get_column_letter(i)   # ← MergedCell 문제 우회

        for 셀 in 열:
            try:
                if 셀.value:
                    최대길이 = max(최대길이, len(str(셀.value)))
            except:
                pass   # 병합 셀은 건너뜀

        ws.column_dimensions[열이름].width = 최대길이 + 4


# ④ 시트 1: 전체 버그 목록
def 시트_전체목록(wb, df):
    ws = wb.active
    ws.title = "전체 버그 목록"

    # 헤더
    ws.append(list(df.columns))
    헤더_스타일(ws)

    # 데이터
    for _, 행 in df.iterrows():
        ws.append(list(행))
        현재행 = ws.max_row

        # 심각도별 색상
        심각도 = 행["심각도"]
        if 심각도 in 색상:
            for 셀 in ws[현재행]:
                셀.fill = PatternFill("solid", fgColor=색상[심각도])

    열너비_조정(ws)
    return ws


# ⑤ 시트 2: 담당자별 현황
def 시트_담당자별(wb, df):
    ws = wb.create_sheet(title="담당자별 현황")

    담당자통계 = df.groupby(["담당자", "상태"]).size().unstack(fill_value=0)

    ws.append(["담당자"] + list(담당자통계.columns))
    헤더_스타일(ws)

    for 담당자, 행 in 담당자통계.iterrows():
        ws.append([담당자] + list(행))
        현재행 = ws.max_row
        for 셀 in ws[현재행]:
            셀.alignment = Alignment(horizontal="center")

    # 차트 추가
    차트 = BarChart()
    차트.title    = "담당자별 버그 현황"
    차트.y_axis.title = "건수"
    차트.x_axis.title = "담당자"

    데이터범위 = Reference(ws,
        min_col=2,
        max_col=ws.max_column,
        min_row=1,
        max_row=ws.max_row
    )
    레이블범위 = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

    차트.add_data(데이터범위, titles_from_data=True)
    차트.set_categories(레이블범위)
    ws.add_chart(차트, "F2")

    열너비_조정(ws)
    return ws


# ⑥ 시트 3: 심각도별 통계
def 시트_심각도별(wb, df):
    ws = wb.create_sheet(title="심각도별 통계")

    심각도통계 = df["심각도"].value_counts()

    ws.append(["심각도", "건수"])
    헤더_스타일(ws)

    for 심각도, 건수 in 심각도통계.items():
        ws.append([심각도, 건수])
        현재행 = ws.max_row
        if 심각도 in 색상:
            for 셀 in ws[현재행]:
                셀.fill      = PatternFill("solid", fgColor=색상[심각도])
                셀.font      = Font(color="FFFFFF", bold=True)
                셀.alignment = Alignment(horizontal="center")

    열너비_조정(ws)
    return ws


# ⑦ 시트 4: 요약 대시보드
def 시트_대시보드(wb, df):
    ws = wb.create_sheet(title="요약 대시보드")

    총버그     = len(df)
    해결       = len(df[df["상태"] == "해결"])
    미해결     = len(df[df["상태"] == "미해결"])
    진행중     = len(df[df["상태"] == "진행중"])
    해결률     = round(해결 / 총버그 * 100, 1)

    대시보드데이터 = [
        ["📊 QA 버그 리포트 요약", ""],
        ["", ""],
        ["항목", "수치"],
        ["총 버그 수",    총버그],
        ["해결",         해결],
        ["진행중",       진행중],
        ["미해결",       미해결],
        ["해결률",       f"{해결률}%"],
        ["", ""],
        ["심각도별", "건수"],
        ["Critical",    len(df[df["심각도"] == "Critical"])],
        ["Major",       len(df[df["심각도"] == "Major"])],
        ["Minor",       len(df[df["심각도"] == "Minor"])],
    ]

    for 행 in 대시보드데이터:
        ws.append(행)

    # 제목 스타일
    ws["A1"].font      = Font(size=16, bold=True, color="4472C4")
    ws["A1"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A1:B1")

    # 헤더 행 스타일
    for 행번호 in [3, 10]:
        for 셀 in ws[행번호]:
            셀.fill      = PatternFill("solid", fgColor="4472C4")
            셀.font      = Font(color="FFFFFF", bold=True)
            셀.alignment = Alignment(horizontal="center")

    # 해결률 강조
    ws["B8"].font = Font(bold=True, color="70AD47", size=12)

    열너비_조정(ws)
    return ws


# ⑧ 전체 리포트 생성
def 리포트_생성(df):
    결과폴더 = 기준경로 / "결과"
    결과폴더.mkdir(exist_ok=True)

    오늘 = datetime.now().strftime("%Y-%m-%d")
    파일명 = 결과폴더 / f"report_{오늘}.xlsx"

    wb = Workbook()

    시트_전체목록(wb, df)
    시트_담당자별(wb, df)
    시트_심각도별(wb, df)
    시트_대시보드(wb, df)

    wb.save(파일명)
    return 파일명