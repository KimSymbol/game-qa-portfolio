# file_io.py
# 역할: 모든 도구에서 공통으로 사용하는 파일 읽기/쓰기 함수
#
# 지원 형식:
#   입력 - .csv / .tsv / .xlsx / .txt / .log / .json
#   출력 - .csv / .json / .html (도구에서 호출)
#
# 사용법:
#   from common.file_io import 파일_읽기, 결과폴더_생성, NaN_처리
#   from common.file_io import JSON_쓰기, HTML_쓰기

import json as json_module
import pandas as pd
import shutil
import logging
from pathlib import Path
from datetime import datetime
from common.logger import 로거_생성

log: logging.Logger = 로거_생성("common.file_io")

def 파일_읽기(파일명, 기준경로=None):
    """
    파일 형식을 자동 판단해서 읽기

    매개변수:
    - 파일명  : 읽을 파일 이름 또는 경로
    - 기준경로: 상대 경로 기준 (None이면 cwd 기준)

    반환값:
    - DataFrame (csv/tsv/xlsx/json 리스트)
    - 줄 목록 list (txt/log)
    - dict (json 딕셔너리)
    - None: 파일이 없거나 지원하지 않는 형식

    지원 형식:
    - .csv  : UTF-8 / UTF-8-BOM
    - .tsv  : 탭 구분 CSV
    - .xlsx : 엑셀
    - .txt  : 텍스트 (줄 목록 반환)
    - .log  : 로그 텍스트 (줄 목록 반환)
    - .json : JSON 데이터
    """
    경로 = Path(파일명)

    if not 경로.exists() and 기준경로:
        경로 = Path(기준경로) / 파일명

    if not 경로.exists():
        log.error(f"파일을 찾을 수 없음: {파일명}")
        return None

    확장자 = 경로.suffix.lower()

    try:
        if 확장자 == ".csv":
            df = pd.read_csv(경로, encoding="utf-8-sig")
            log.info(f"파일 로딩 완료: {len(df)}건 (.csv) - {경로.name}")
            return df

        elif 확장자 == ".tsv":
            df = pd.read_csv(경로, encoding="utf-8-sig", sep="\t")
            log.info(f"파일 로딩 완료: {len(df)}건 (.tsv) - {경로.name}")
            return df

        elif 확장자 == ".xlsx":
            df = pd.read_excel(경로)
            log.info(f"파일 로딩 완료: {len(df)}건 (.xlsx) - {경로.name}")
            return df

        elif 확장자 in [".txt", ".log"]:
            with open(경로, "r", encoding="utf-8") as f:
                줄목록 = f.readlines()
            log.info(f"파일 로딩 완료: {len(줄목록)}줄 ({확장자}) - {경로.name}")
            return 줄목록

        elif 확장자 == ".json":
            with open(경로, "r", encoding="utf-8") as f:
                데이터 = json_module.load(f)
            if isinstance(데이터, list):
                df = pd.DataFrame(데이터)
                log.info(f"파일 로딩 완료: {len(df)}건 (.json) - {경로.name}")
                return df
            else:
                log.warning(f"JSON이 리스트 형태가 아님 → 원본 반환")
                return 데이터

        else:
            log.error(f"지원하지 않는 형식: {확장자}")
            log.error(f"   지원 형식: csv / tsv / xlsx / txt / log / json")
            return None

    except FileNotFoundError:
        log.error(f"파일을 찾을 수 없음: {경로}")
        return None
    except pd.errors.EmptyDataError:
        log.error(f"빈 파일: {경로}")
        return None
    except UnicodeDecodeError as e:
        log.error(f"인코딩 오류: {경로}")
        log.error(f"   utf-8 외 다른 인코딩일 수 있어요 - {e}")
        return None
    except json_module.JSONDecodeError as e:
        log.error(f"JSON 형식 오류: {경로} - {e}")
        return None
    except Exception as e:
        log.error(f"파일 읽기 실패: {경로} - {type(e).__name__}: {e}")
        return None


def 결과폴더_생성(기준경로):
    """결과 폴더가 없으면 자동 생성"""
    폴더 = Path(기준경로) / "결과"
    폴더.mkdir(exist_ok=True)
    return 폴더


def NaN_처리(df, 컬럼목록=None):
    """DataFrame의 NaN 값을 빈 문자열로 변환"""
    if 컬럼목록:
        for 컬럼 in 컬럼목록:
            if 컬럼 in df.columns:
                df[컬럼] = df[컬럼].fillna("")
    else:
        df = df.fillna("")
    return df


def JSON_쓰기(파일경로, 데이터, 들여쓰기=4):
    """
    DataFrame 또는 딕셔너리/리스트를 JSON 파일로 저장

    매개변수:
    - 파일경로 : 저장할 파일 경로
    - 데이터   : DataFrame 또는 dict/list
    - 들여쓰기 : JSON 들여쓰기 칸 수 (기본 4)
    """
    if isinstance(데이터, pd.DataFrame):
        데이터 = 데이터.to_dict(orient="records")

    with open(파일경로, "w", encoding="utf-8") as f:
        json_module.dump(데이터, f, ensure_ascii=False, indent=들여쓰기)


def HTML_쓰기(파일경로, 제목, 본문):
    """
    HTML 리포트 파일 저장 (기본 스타일 포함)

    매개변수:
    - 파일경로: 저장할 파일 경로
    - 제목   : HTML 제목
    - 본문   : HTML 본문 내용 (HTML 문자열)
    """
    HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{제목}</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
            line-height: 1.6;
        }}
        h1 {{
            color: #4472C4;
            border-bottom: 3px solid #4472C4;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #4472C4;
            margin-top: 30px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px 12px;
            text-align: left;
        }}
        th {{
            background-color: #4472C4;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .Critical {{ background-color: #FF0000; color: white; font-weight: bold; }}
        .High     {{ background-color: #FF6600; color: white; font-weight: bold; }}
        .Medium   {{ background-color: #FFC000; color: white; font-weight: bold; }}
        .Low      {{ background-color: #70AD47; color: white; font-weight: bold; }}
        .해결     {{ background-color: #70AD47; color: white; font-weight: bold; }}
        .진행중   {{ background-color: #FFC000; color: white; font-weight: bold; }}
        .미해결   {{ background-color: #FF0000; color: white; font-weight: bold; }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #4472C4;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #999;
            font-size: 0.9em;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>{제목}</h1>
    {본문}
    <div class="footer">
        Generated by QA Tools | <span id="date"></span>
        <script>document.getElementById('date').textContent = new Date().toLocaleString();</script>
    </div>
</body>
</html>"""

    with open(파일경로, "w", encoding="utf-8") as f:
        f.write(HTML)


def PDF_쓰기(파일경로, 제목, df, 요약정보=None):
    """
    DataFrame을 PDF 리포트로 저장
    한글 폰트 지원

    매개변수:
    - 파일경로 : 저장할 PDF 파일 경로
    - 제목     : PDF 제목
    - df       : DataFrame
    - 요약정보 : 요약 텍스트 (dict 형태, 예: {"총 버그 수": 20, "해결률": "50%"})
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, PageBreak
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    # 한글 폰트 등록 (Windows 기본 폰트)
    한글폰트경로목록 = [
        "C:/Windows/Fonts/malgun.ttf",      # 맑은 고딕
        "C:/Windows/Fonts/gulim.ttc",       # 굴림
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # Mac
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
    ]

    한글폰트등록됨 = False
    for 폰트경로 in 한글폰트경로목록:
        if os.path.exists(폰트경로):
            try:
                pdfmetrics.registerFont(TTFont("Korean", 폰트경로))
                한글폰트등록됨 = True
                break
            except:
                continue

    폰트명 = "Korean" if 한글폰트등록됨 else "Helvetica"

    # PDF 문서 생성 (가로 방향, 데이터 많으면 가독성 좋음)
    doc = SimpleDocTemplate(
        str(파일경로),
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    스토리 = []
    스타일 = getSampleStyleSheet()

    # 제목 스타일
    제목스타일 = ParagraphStyle(
        "title",
        parent=스타일["Heading1"],
        fontName=폰트명,
        fontSize=18,
        textColor=colors.HexColor("#4472C4"),
        spaceAfter=20
    )
    스토리.append(Paragraph(제목, 제목스타일))

    # 요약 정보 추가
    if 요약정보:
        요약스타일 = ParagraphStyle(
            "summary",
            fontName=폰트명,
            fontSize=11,
            textColor=colors.HexColor("#333333"),
            spaceAfter=10
        )
        for 키, 값 in 요약정보.items():
            스토리.append(Paragraph(f"<b>{키}:</b> {값}", 요약스타일))
        스토리.append(Spacer(1, 0.5*cm))

    # 테이블 데이터 준비
    헤더 = list(df.columns)
    데이터 = [헤더]
    for _, 행 in df.iterrows():
        데이터.append([str(값) if 값 != "" and str(값) != "nan" else "" for 값 in 행])

    # 테이블 스타일
    table = Table(데이터, repeatRows=1)
    table.setStyle(TableStyle([
        # 헤더 스타일
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), 폰트명),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        # 본문 스타일
        ("FONTNAME", (0, 1), (-1, -1), 폰트명),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # 격자선
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        # 행 배경색 (지그재그)
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F8F9FA")]),
    ]))

    스토리.append(table)
    doc.build(스토리)


def 타임스탬프():
    """
    현재 시간을 파일명용 문자열로 반환
    형식: YYYY-MM-DD_HH-MM-SS

    예시: 2026-06-17_14-30-22
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def 날짜():
    """
    현재 날짜만 반환
    형식: YYYY-MM-DD

    예시: 2026-06-17
    """
    return datetime.now().strftime("%Y-%m-%d")


def Latest_복사(원본경로, 접두사="report"):
    """
    생성된 파일을 'latest' 이름으로 복사
    가장 최근 리포트를 빠르게 찾을 수 있게 함

    매개변수:
    - 원본경로: 복사할 원본 파일 경로
    - 접두사  : latest 파일 이름 접두사 (기본 "report")

    예시:
    - report_2026-06-17_14-30-22.xlsx 가 생성되면
    - report_latest.xlsx 로도 복사됨
    """
    원본 = Path(원본경로)
    확장자 = 원본.suffix
    Latest경로 = 원본.parent / f"{접두사}_latest{확장자}"

    try:
        shutil.copy(원본, Latest경로)
    except Exception as e:
        log.warning(f"Latest 복사 실패: {e}")