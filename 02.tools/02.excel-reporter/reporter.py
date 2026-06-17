# reporter.py
# 역할: CSV 버그 데이터를 읽어 전문적인 엑셀 리포트를 생성하는 모듈
# 다른 모듈(main.py)에서 import해서 사용

import pandas as pd        # CSV 읽기 및 데이터 분석
from pathlib import Path   # 경로 관리 - 파일/폴더 탐색 및 생성
from openpyxl import Workbook                             # 엑셀 파일 생성
from openpyxl.styles import PatternFill, Font, Alignment  # 엑셀 스타일
from openpyxl.chart import BarChart, Reference            # 엑셀 차트
from openpyxl.utils import get_column_letter              # 열 이름 변환
from datetime import datetime                             # 날짜/시간

# reporter.py 가 있는 폴더를 기준 경로로 설정
# → 어디서 실행해도 파일을 올바른 위치에서 찾음
기준경로 = Path(__file__).parent

# ── 심각도/상태별 색상 정의 ──
# 엑셀 셀 배경색으로 사용하는 HEX 코드
색상 = {
    "Critical": "FF0000",   # 빨강 - 즉시 처리 필요
    "Major"   : "FFC000",   # 노랑 - 우선 처리
    "Minor"   : "70AD47",   # 초록 - 일반 처리
    "해결"    : "70AD47",   # 초록 - 완료
    "진행중"  : "FFC000",   # 노랑 - 처리 중
    "미해결"  : "FF0000",   # 빨강 - 미처리
    "헤더"    : "4472C4",   # 파랑 - 헤더 배경
}


# ────────────────────────────────────────
# ① CSV 읽기
# ────────────────────────────────────────
def 데이터_읽기(파일명):
    """
    CSV 파일을 읽어서 DataFrame으로 반환

    매개변수:
    - 파일명: 읽을 CSV 파일 이름 (예: "bugs.csv")
              기준경로(reporter.py 위치) 기준으로 찾음

    반환값:
    - DataFrame: 버그 데이터가 담긴 pandas DataFrame
    - None: 파일이 없을 때

    지원 형식:
    - UTF-8 인코딩 CSV 파일 (.csv)
    - 첫 번째 줄이 헤더여야 함
    - 필수 컬럼: 버그ID, 제목, 심각도, 담당자, 상태, 발견일
    - 선택 컬럼: 해결일 (미해결이면 비워도 됨)
    """
    경로 = 기준경로 / 파일명
    if not 경로.exists():
        print("❌ 파일이 없어요:", 경로)
        return None
    df = pd.read_csv(경로, encoding="utf-8")
    print(f"✅ 데이터 로딩 완료: {len(df)}건")
    return df


# ────────────────────────────────────────
# ② 헤더 스타일 적용
# ────────────────────────────────────────
def 헤더_스타일(ws, 행번호=1):
    """
    지정한 행을 헤더 스타일로 꾸밈
    배경: 파란색 / 글씨: 흰색 굵게 / 정렬: 가운데

    매개변수:
    - ws    : openpyxl 워크시트 객체
    - 행번호: 스타일 적용할 행 번호 (기본값 1)
    """
    for 셀 in ws[행번호]:
        셀.fill      = PatternFill("solid", fgColor=색상["헤더"])
        셀.font      = Font(color="FFFFFF", bold=True)
        셀.alignment = Alignment(horizontal="center")


# ────────────────────────────────────────
# ③ 열 너비 자동 조정
# ────────────────────────────────────────
def 열너비_조정(ws):
    """
    워크시트의 각 열 너비를 내용 길이에 맞게 자동 조정

    매개변수:
    - ws: openpyxl 워크시트 객체

    동작:
    - 각 열의 모든 셀 중 가장 긴 내용 기준으로 너비 설정
    - 여백 4 추가해서 답답하지 않게
    - MergedCell(병합 셀)은 try/except로 건너뜀
    - get_column_letter 사용으로 병합 셀 에러 방지
    """
    for i, 열 in enumerate(ws.columns, 1):
        최대길이 = 0
        열이름  = get_column_letter(i)

        for 셀 in 열:
            try:
                if 셀.value:
                    최대길이 = max(최대길이, len(str(셀.value)))
            except:
                pass  # 병합 셀 건너뜀

        ws.column_dimensions[열이름].width = 최대길이 + 4


# ────────────────────────────────────────
# ④ 시트 1: 전체 버그 목록
# ────────────────────────────────────────
def 시트_전체목록(wb, df):
    """
    CSV의 전체 데이터를 심각도별 색상으로 표시하는 시트 생성

    매개변수:
    - wb: openpyxl Workbook 객체
    - df: 버그 데이터 DataFrame

    색상 규칙:
    - Critical 행 → 빨간 배경
    - Major 행    → 노란 배경
    - Minor 행    → 초록 배경
    """
    ws = wb.active
    ws.title = "전체 버그 목록"

    # CSV 헤더를 그대로 첫 번째 행으로 사용
    ws.append(list(df.columns))
    헤더_스타일(ws)

    # 데이터 행 추가 + 심각도별 색상 적용
    for _, 행 in df.iterrows():
        ws.append(list(행))
        현재행 = ws.max_row
        심각도 = 행["심각도"]
        if 심각도 in 색상:
            for 셀 in ws[현재행]:
                셀.fill = PatternFill("solid", fgColor=색상[심각도])

    열너비_조정(ws)
    return ws


# ────────────────────────────────────────
# ⑤ 시트 2: 담당자별 현황
# ────────────────────────────────────────
def 시트_담당자별(wb, df):
    """
    담당자별 버그 상태 현황과 막대 차트를 생성하는 시트

    매개변수:
    - wb: openpyxl Workbook 객체
    - df: 버그 데이터 DataFrame

    동작:
    - groupby로 담당자 × 상태 교차 집계
    - 막대 차트로 시각화 (F2 위치에 삽입)
    """
    ws = wb.create_sheet(title="담당자별 현황")

    # 담당자 × 상태 교차 집계
    # fill_value=0 → 해당 조합이 없으면 0으로 채움
    담당자통계 = df.groupby(["담당자", "상태"]).size().unstack(fill_value=0)

    ws.append(["담당자"] + list(담당자통계.columns))
    헤더_스타일(ws)

    for 담당자, 행 in 담당자통계.iterrows():
        ws.append([담당자] + list(행))
        현재행 = ws.max_row
        for 셀 in ws[현재행]:
            셀.alignment = Alignment(horizontal="center")

    # 막대 차트 생성
    차트 = BarChart()
    차트.title        = "담당자별 버그 현황"
    차트.y_axis.title = "건수"
    차트.x_axis.title = "담당자"

    데이터범위 = Reference(ws,
        min_col=2, max_col=ws.max_column,
        min_row=1, max_row=ws.max_row
    )
    레이블범위 = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

    차트.add_data(데이터범위, titles_from_data=True)
    차트.set_categories(레이블범위)
    ws.add_chart(차트, "F2")  # F2 위치에 차트 삽입

    열너비_조정(ws)
    return ws


# ────────────────────────────────────────
# ⑥ 시트 3: 심각도별 통계
# ────────────────────────────────────────
def 시트_심각도별(wb, df):
    """
    심각도별 버그 건수를 색상 구분해서 표시하는 시트

    매개변수:
    - wb: openpyxl Workbook 객체
    - df: 버그 데이터 DataFrame
    """
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


# ────────────────────────────────────────
# ⑦ 시트 4: 요약 대시보드
# ────────────────────────────────────────
def 시트_대시보드(wb, df):
    """
    총 버그 수, 해결률 등 핵심 지표를 한눈에 보여주는 대시보드 시트

    매개변수:
    - wb: openpyxl Workbook 객체
    - df: 버그 데이터 DataFrame

    표시 항목:
    - 총 버그 수 / 해결 / 진행중 / 미해결 건수
    - 해결률 (해결 / 전체 × 100)
    - 심각도별 건수 (Critical / Major / Minor)
    """
    ws = wb.create_sheet(title="요약 대시보드")

    # 핵심 지표 계산
    총버그 = len(df)
    해결   = len(df[df["상태"] == "해결"])
    미해결 = len(df[df["상태"] == "미해결"])
    진행중 = len(df[df["상태"] == "진행중"])
    해결률 = round(해결 / 총버그 * 100, 1)

    대시보드데이터 = [
        ["📊 QA 버그 리포트 요약", ""],
        ["", ""],
        ["항목",     "수치"],
        ["총 버그 수", 총버그],
        ["해결",      해결],
        ["진행중",    진행중],
        ["미해결",    미해결],
        ["해결률",    f"{해결률}%"],
        ["", ""],
        ["심각도별",  "건수"],
        ["Critical", len(df[df["심각도"] == "Critical"])],
        ["Major",    len(df[df["심각도"] == "Major"])],
        ["Minor",    len(df[df["심각도"] == "Minor"])],
    ]

    for 행 in 대시보드데이터:
        ws.append(행)

    # 제목 스타일 (A1 셀)
    ws["A1"].font      = Font(size=16, bold=True, color="4472C4")
    ws["A1"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A1:B1")  # A1:B1 병합

    # 소제목 헤더 행 스타일 (3행, 10행)
    for 행번호 in [3, 10]:
        for 셀 in ws[행번호]:
            셀.fill      = PatternFill("solid", fgColor="4472C4")
            셀.font      = Font(color="FFFFFF", bold=True)
            셀.alignment = Alignment(horizontal="center")

    # 해결률 강조 (초록 굵게 크게)
    ws["B8"].font = Font(bold=True, color="70AD47", size=12)

    열너비_조정(ws)
    return ws


# ────────────────────────────────────────
# ⑧ 전체 리포트 생성
# ────────────────────────────────────────
def 리포트_생성(df):
    """
    4개 시트로 구성된 전체 엑셀 리포트 생성 및 저장

    매개변수:
    - df: 버그 데이터 DataFrame

    반환값:
    - 저장된 파일 경로 (Path 객체)

    저장 위치: 결과/report_YYYY-MM-DD.xlsx

    시트 구성:
    1. 전체 버그 목록 - 심각도별 색상 구분
    2. 담당자별 현황 - 교차 집계 + 막대 차트
    3. 심각도별 통계 - Critical/Major/Minor 집계
    4. 요약 대시보드 - 해결률 등 핵심 지표
    """
    결과폴더 = 기준경로 / "결과"
    결과폴더.mkdir(exist_ok=True)

    오늘   = datetime.now().strftime("%Y-%m-%d")
    파일명 = 결과폴더 / f"report_{오늘}.xlsx"

    wb = Workbook()

    시트_전체목록(wb, df)
    시트_담당자별(wb, df)
    시트_심각도별(wb, df)
    시트_대시보드(wb, df)

    wb.save(파일명)
    return 파일명