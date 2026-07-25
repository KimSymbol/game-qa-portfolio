# 역할: NUnit 테스트 결과를 Allure 리포트 형식으로 변환

import hashlib
import json
import os
import platform
import shutil
import time
import uuid

from dotenv import load_dotenv


# ── 1. 변수 선언부 ──────────────────────────────────

load_dotenv()

ALLURE_RESULTS_DIR = "allure-results"

UNITY_VERSION = os.getenv("UNITY_VERSION", "6000.3.8f1")

# Allure 가 인식하는 테스트 상태값
STATUS_PASSED = "passed"
STATUS_FAILED = "failed"

# 초 단위 시간을 Allure 가 쓰는 밀리초로 변환
SECONDS_TO_MS = 1000


# ── 2. 함수 선언부 ──────────────────────────────────

def _history_id(full_name):
    """
    테스트 고유 식별자 생성.

    Allure 는 이 값으로 실행 이력을 추적하므로
    같은 테스트는 항상 같은 값이어야 한다.
    """
    return hashlib.md5(full_name.encode("utf-8")).hexdigest()


def _build_labels(case):
    """Allure 리포트의 분류 라벨을 생성한다."""
    return [
        {"name": "epic", "value": "Unity QA"},
        {"name": "feature", "value": case.suite},
        {"name": "story", "value": f"{case.test_id} {case.test_name}"},
        {"name": "suite", "value": case.suite},
        {"name": "testClass", "value": case.suite},
        {"name": "framework", "value": "Unity Test Framework"},
        {"name": "language", "value": "C#"},
    ]


def _build_result(case, start_ms):
    """개별 테스트 결과를 Allure JSON 구조로 변환한다."""
    duration_ms = int(case.duration * SECONDS_TO_MS)

    result = {
        "uuid": str(uuid.uuid4()),
        "historyId": _history_id(case.full_name),
        "name": f"{case.test_id} {case.test_name}",
        "fullName": case.full_name,
        "status": STATUS_PASSED if case.passed else STATUS_FAILED,
        "stage": "finished",
        "start": start_ms,
        "stop": start_ms + duration_ms,
        "labels": _build_labels(case),
    }

    if not case.passed:
        result["statusDetails"] = {
            "known": False,
            "muted": False,
            "flaky": False,
            "message": case.message,
            "trace": case.stack_trace,
        }

    return result


def _write_environment():
    """
    Allure 리포트 상단에 표시할 환경 정보를 기록한다.

    실행 환경을 명시해야 로컬/CI 결과를 구분할 수 있다.
    """
    properties = {
        "OS": f"{platform.system()} {platform.release()}",
        "Unity": UNITY_VERSION,
        "Test.Framework": "Unity Test Framework (NUnit)",
        "Test.Mode": "PlayMode / batchmode",
        "Test.Target": "Sentaur Survivors",
    }

    path = os.path.join(ALLURE_RESULTS_DIR, "environment.properties")

    with open(path, "w", encoding="utf-8") as file:
        for key, value in properties.items():
            file.write(f"{key}={value}\n")


def generate(result):
    """
    테스트 결과를 Allure 결과 파일로 생성한다.

    매개변수:
    - result: unity_runner.parse_results() 가 반환한 TestRunResult
    """
    # 이전 실행 결과가 섞이지 않도록 폴더를 초기화한다
    if os.path.exists(ALLURE_RESULTS_DIR):
        shutil.rmtree(ALLURE_RESULTS_DIR)
    os.makedirs(ALLURE_RESULTS_DIR)

    start_ms = int(time.time() * SECONDS_TO_MS)

    for case in result.cases:
        data = _build_result(case, start_ms)
        path = os.path.join(ALLURE_RESULTS_DIR, f"{data['uuid']}-result.json")

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    _write_environment()

    print(f"[Allure] 결과 {len(result.cases)}건 생성: {ALLURE_RESULTS_DIR}")