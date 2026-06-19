# 역할: 모든 도구에서 공통으로 사용하는 로깅 시스템
#
# 사용법:
#   from common.logger import 로거_생성
#   log = 로거_생성("excel-reporter")
#   log.info("✅ 파일 로딩 완료")
#   log.error("❌ 파일이 없어요")

import logging
from pathlib import Path
from datetime import datetime

from common.config import 설정


# 이미 생성된 로거 캐시 (중복 생성 방지)
_로거캐시 = {}


def 로거_생성(이름="QA-Tools", 로그파일=True):
    """
    로거 생성 및 반환

    매개변수:
    - 이름     : 로거 이름 (도구명 권장: "excel-reporter")
    - 로그파일 : 로그 파일 저장 여부 (기본 True)

    반환값:
    - logging.Logger 객체

    동작:
    - 콘솔 + 파일 동시 출력
    - 로그 파일: 02.tools/logs/{이름}_YYYY-MM-DD.log
    - 같은 이름으로 다시 호출하면 기존 로거 반환 (중복 방지)
    """
    # 캐시에 있으면 그대로 반환
    if 이름 in _로거캐시:
        return _로거캐시[이름]

    # 새 로거 생성
    로거 = logging.getLogger(이름)

    # 로그 레벨 설정
    레벨문자열 = 설정.get("로그_레벨", "INFO").upper()
    레벨 = getattr(logging, 레벨문자열, logging.INFO)
    로거.setLevel(레벨)

    # 기존 핸들러 제거 (중복 방지)
    로거.handlers.clear()

    # 포맷 정의
    포맷 = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 핸들러
    콘솔핸들러 = logging.StreamHandler()
    콘솔핸들러.setFormatter(포맷)
    로거.addHandler(콘솔핸들러)

    # 파일 핸들러
    if 로그파일:
        # 02.tools/logs/ 폴더에 저장
        로그폴더 = Path(__file__).parent.parent / 설정.get("로그_폴더명", "logs")
        로그폴더.mkdir(exist_ok=True)

        오늘 = datetime.now().strftime("%Y-%m-%d")
        로그파일경로 = 로그폴더 / f"{이름}_{오늘}.log"

        파일핸들러 = logging.FileHandler(로그파일경로, encoding="utf-8")
        파일핸들러.setFormatter(포맷)
        로거.addHandler(파일핸들러)

    # 캐시에 저장
    _로거캐시[이름] = 로거
    return 로거