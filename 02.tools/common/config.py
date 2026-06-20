# 역할: 설정 파일(config.json)을 로딩하고 관리
#
# 사용법:
#   from common.config import 설정
#   값 = 설정.get("타임스탬프_형식", "%Y-%m-%d_%H-%M-%S")

import json
from pathlib import Path

# config.py 가 있는 폴더 (common)
_기준경로 = Path(__file__).parent
_설정파일 = _기준경로 / "config.json"

# 기본 설정 (config.json 없을 때 사용)
_기본설정 = {
    "결과_폴더명": "결과",
    "타임스탬프_형식": "%Y-%m-%d_%H-%M-%S",
    "기본_인코딩": "utf-8-sig",
    "로그_레벨": "INFO",
    "로그_폴더명": "logs",
    "latest_복사_사용": True,
    "기본_엑셀_시트_최대너비": 60,
    "한글_폰트_경로": [
        "C:/Windows/Fonts/malgun.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    ],
    "도구별_접두사": {
        "excel-reporter": "report",
        "data-validator": "validation_report",
        "log-analyzer": "bug_report",
        "md-report-gen": "ALL_BUGS"
    }
}


def _설정_로딩():
    """
    config.json 파일을 로딩
    파일이 없으면 기본 설정 반환
    """
    if not _설정파일.exists():
        print(f"[WARN]  설정 파일 없음 → 기본 설정 사용")
        return _기본설정

    try:
        with open(_설정파일, "r", encoding="utf-8") as f:
            로딩된설정 = json.load(f)
        # 누락된 키는 기본값으로 채움
        for 키, 값 in _기본설정.items():
            if 키 not in 로딩된설정:
                로딩된설정[키] = 값
        return 로딩된설정
    except json.JSONDecodeError as e:
        print(f"[WARN]  설정 파일 형식 오류: {e}")
        print(f"   기본 설정으로 동작합니다")
        return _기본설정
    except Exception as e:
        print(f"[WARN]  설정 파일 로딩 실패: {e}")
        return _기본설정


# 모듈 import 시 자동 로딩
설정 = _설정_로딩()