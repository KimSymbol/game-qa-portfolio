# 공통 모듈 (common)

모든 QA 도구에서 공유하는 핵심 모듈입니다.
파일 입출력, 엑셀 스타일, 로깅, 설정 관리를 담당합니다.

---

## 구조

```
common/
├── __init__.py        # 패키지 초기화
├── file_io.py         # 파일 읽기/쓰기 (다양한 형식 지원)
├── excel_style.py     # 엑셀 공통 스타일 (색상, 헤더, 열너비)
├── logger.py          # 로깅 시스템
├── config.py          # 설정 로딩
├── config.json        # 전역 설정 파일
└── README.md
```

---

## 모듈별 기능

### file_io.py — 파일 입출력

모든 도구에서 공통으로 사용하는 읽기/쓰기 함수입니다.

#### 사용법

```python
from common.file_io import 파일_읽기, 결과폴더_생성, NaN_처리
from common.file_io import 타임스탬프, Latest_복사
from common.file_io import JSON_쓰기, HTML_쓰기, PDF_쓰기
```

#### 함수 목록

| 함수 | 역할 | 반환값 |
|------|------|--------|
| `파일_읽기(파일명, 기준경로)` | 파일 형식 자동 판단 후 읽기 | DataFrame / list / dict |
| `결과폴더_생성(기준경로)` | 결과 폴더 자동 생성 | Path |
| `NaN_처리(df, 컬럼목록)` | NaN → 빈 문자열 변환 | DataFrame |
| `타임스탬프()` | 파일명용 현재 시간 | str (YYYY-MM-DD_HH-MM-SS) |
| `날짜()` | 현재 날짜 | str (YYYY-MM-DD) |
| `Latest_복사(원본경로, 접두사)` | latest 파일 자동 복사 | None |
| `JSON_쓰기(파일경로, 데이터)` | DataFrame/dict → JSON 저장 | None |
| `HTML_쓰기(파일경로, 제목, 본문)` | HTML 리포트 저장 | None |
| `PDF_쓰기(파일경로, 제목, df, 요약)` | PDF 리포트 저장 | None |

#### 지원 입력 형식

| 확장자 | 반환값 | 인코딩 |
|--------|--------|--------|
| `.csv` | DataFrame | utf-8-sig |
| `.tsv` | DataFrame | utf-8-sig (탭 구분) |
| `.xlsx` | DataFrame | 자동 |
| `.txt` | list (줄 목록) | utf-8 |
| `.log` | list (줄 목록) | utf-8 |
| `.json` | DataFrame (리스트) / dict | utf-8 |

#### 경로 탐색 순서

```
1. 절대 경로 또는 cwd 기준 상대 경로
2. 기준경로(도구 폴더) 기준 상대 경로
```

---

### excel_style.py — 엑셀 스타일

모든 엑셀 리포트에서 공유하는 색상, 스타일 함수입니다.

#### 사용법

```python
from common.excel_style import 색상, 우선순위_색상
from common.excel_style import 헤더_스타일, 셀_색상, 행_색상
from common.excel_style import 색상_가져오기, 열너비_조정
```

#### 함수 목록

| 함수 | 역할 |
|------|------|
| `헤더_스타일(ws, 행번호)` | 헤더 행 스타일 (파란 배경, 흰 글씨) |
| `셀_색상(셀, 배경색, 글자색, 굵게, 가운데)` | 개별 셀 스타일 |
| `행_색상(ws, 행번호, 배경색, 글자색, 굵게)` | 행 전체 스타일 |
| `색상_가져오기(값, 기본색)` | 값에 해당하는 색상 코드 반환 |
| `열너비_조정(ws, 최대너비)` | 열 너비 자동 조정 (병합 셀 안전) |

#### 색상 맵

```python
색상 = {
    # 심각도
    "Critical": "FF0000",    # 빨강
    "High"    : "FF6600",    # 주황
    "Medium"  : "FFC000",    # 노랑
    "Low"     : "70AD47",    # 초록

    # 상태
    "해결"    : "70AD47",    # 초록
    "진행중"  : "FFC000",    # 노랑
    "미해결"  : "FF0000",    # 빨강

    # 테스트 결과
    "Pass"    : "70AD47",
    "Fail"    : "FF0000",
    "Block"   : "FFC000",
    "Skip"    : "BFBFBF",

    # 로그 유형
    "ERROR"   : "FF0000",
    "WARNING" : "FFC000",
    "INFO"    : "70AD47",

    # 공통
    "헤더"    : "4472C4",    # 파란
    "기본"    : "BFBFBF",    # 회색
}
```

---

### logger.py — 로깅 시스템

모든 도구의 실행 이력을 파일 + 콘솔에 동시 출력합니다.

#### 사용법

```python
from common.logger import 로거_생성

log = 로거_생성("도구이름")

log.info("정상 동작")
log.warning("경고")
log.error("에러 발생")
log.debug("디버그 정보")
```

#### 로그 파일 위치

```
02.tools/logs/
├── test-data-gen_2026-06-20.log
├── data-validator_2026-06-20.log
├── excel-reporter_2026-06-20.log
└── ...
```

#### 로그 출력 형식

```
2026-06-20 14:30:22 [INFO] [excel-reporter] 리포트 생성 시작: bugs.csv
2026-06-20 14:30:22 [ERROR] [data-validator] 파일을 찾을 수 없음: test.csv
```

#### 로그 레벨

| 레벨 | 용도 |
|------|------|
| `INFO` | 정상 동작 알림 |
| `WARNING` | 주의사항 (동작은 계속) |
| `ERROR` | 실패/에러 |
| `DEBUG` | 디버그 정보 (기본 숨김) |

---

### config.py + config.json — 설정 관리

전역 설정을 JSON 파일로 관리합니다.
config.json 이 없으면 기본값으로 동작합니다.

#### config.json 항목

```json
{
    "결과_폴더명": "결과",
    "타임스탬프_형식": "%Y-%m-%d_%H-%M-%S",
    "기본_인코딩": "utf-8-sig",
    "로그_레벨": "INFO",
    "로그_폴더명": "logs",
    "latest_복사_사용": true,
    "기본_엑셀_시트_최대너비": 60,
    "한글_폰트_경로": [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc"
    ]
}
```

---

## 유지보수 & 커스터마이즈 가이드

### 1. 새 색상 추가

`excel_style.py` 의 `색상` 딕셔너리에 추가하면 모든 도구에 자동 반영.

```python
# excel_style.py
색상 = {
    # 기존 ...
    "Trivial": "999999",    # 새 심각도 추가
}
```

### 2. 새 입력 형식 지원

`file_io.py` 의 `파일_읽기()` 함수에 분기 추가.

```python
# file_io.py 의 파일_읽기() 안에 추가
elif 확장자 == ".yaml":
    import yaml
    with open(경로, "r", encoding="utf-8") as f:
        데이터 = yaml.safe_load(f)
    return 데이터
```

### 3. 새 출력 형식 추가

`file_io.py` 에 쓰기 함수 추가.

```python
def XML_쓰기(파일경로, 데이터):
    """DataFrame → XML 저장"""
    # 구현
```

### 4. 로그 레벨 변경

`config.json` 의 `로그_레벨` 만 변경.

```json
{
    "로그_레벨": "DEBUG"
}
```

### 5. HTML 리포트 스타일 변경

`file_io.py` 의 `HTML_쓰기()` 함수 내부 CSS 수정.
한 곳만 수정하면 모든 도구의 HTML 출력에 일괄 반영됩니다.

### 6. PDF 한글 폰트 변경

`file_io.py` 의 `PDF_쓰기()` 함수 또는 `config.json` 의 폰트 경로 수정.

```json
{
    "한글_폰트_경로": [
        "C:/Windows/Fonts/NanumGothic.ttf"
    ]
}
```

### 7. 타임스탬프 형식 변경

`config.json` 의 `타임스탬프_형식` 수정.

```json
{
    "타임스탬프_형식": "%Y%m%d_%H%M%S"
}
```

결과: `report_20260620_143022.xlsx`

### 8. 결과 폴더명 변경

`config.json` 의 `결과_폴더명` 수정.

```json
{
    "결과_폴더명": "output"
}
```

결과: 모든 도구가 `output/` 폴더에 저장

---

## 다른 도구에서 사용하는 방법

```python
import sys
from pathlib import Path

# 02.tools 폴더를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# 필요한 모듈만 import
from common.file_io import 파일_읽기, 결과폴더_생성, 타임스탬프, Latest_복사
from common.excel_style import 헤더_스타일, 행_색상, 색상_가져오기, 열너비_조정
from common.logger import 로거_생성

# 로거 생성
log = 로거_생성("내도구이름")

# 파일 읽기
df = 파일_읽기("data.csv", 기준경로)

# 결과 폴더 생성
결과폴더 = 결과폴더_생성(기준경로)

# 타임스탬프 파일명
시각 = 타임스탬프()
파일명 = 결과폴더 / f"result_{시각}.xlsx"

# latest 복사
Latest_복사(파일명, "result")
```

---

## 트러블슈팅

### 1. `ModuleNotFoundError: No module named 'common'`

`sys.path.insert(0, ...)` 가 `02.tools` 폴더를 가리키는지 확인.

```python
# 각 도구의 모듈 파일 (.py) 상단에 필수
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### 2. `__pycache__` 캐시 문제

common 모듈 수정 후 반영이 안 되면 캐시 삭제.

```bash
Remove-Item -Recurse -Force common/__pycache__
```

### 3. config.json 형식 오류

JSON 문법 오류 시 기본값으로 자동 동작합니다.
정상 동작하지만 `[WARN] 설정 파일 형식 오류` 메시지가 출력됩니다.