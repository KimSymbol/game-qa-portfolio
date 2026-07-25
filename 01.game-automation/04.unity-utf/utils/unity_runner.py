# 역할: Unity CLI 로 PlayMode 테스트를 실행하고 NUnit XML 결과를 파싱

import os
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from dotenv import load_dotenv


# ── 1. 변수 선언부 ──────────────────────────────────

load_dotenv()

UNITY_EDITOR_PATH = os.getenv("UNITY_EDITOR_PATH")
UNITY_PROJECT_PATH = os.getenv("UNITY_PROJECT_PATH")

RESULTS_DIR = "results"
RESULT_XML = os.path.join(RESULTS_DIR, "results.xml")
UNITY_LOG = os.path.join(RESULTS_DIR, "unity.log")

# Unity 테스트 실행 종료 코드
EXIT_SUCCESS = 0
EXIT_TESTS_FAILED = 2

# 프레임워크가 자동 추가하는 테스트는 집계에서 제외
IGNORED_TEST_PREFIXES = ("Unity.PerformanceTesting",)


# ── 2. 함수 선언부 ──────────────────────────────────

@dataclass
class TestCase:
    """개별 테스트 실행 결과."""

    test_id: str
    test_name: str
    passed: bool
    message: str = ""
    stack_trace: str = ""
    suite: str = ""          # 소속 테스트 클래스
    duration: float = 0.0    # 개별 실행 시간(초)
    full_name: str = ""      # NUnit fullname 원본


@dataclass
class TestRunResult:
    """전체 테스트 실행 결과 집계."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    duration: float = 0.0
    failures: list = field(default_factory=list)
    cases: list = field(default_factory=list)   # 전체 케이스 (Allure 생성용)


def _build_command():
    """Unity CLI 실행 명령을 조립한다."""
    return [
        UNITY_EDITOR_PATH,
        "-runTests",
        "-batchmode",
        "-projectPath", UNITY_PROJECT_PATH,
        "-testPlatform", "PlayMode",
        "-testResults", os.path.abspath(RESULT_XML),
        "-logFile", os.path.abspath(UNITY_LOG),
    ]


def _split_test_name(full_name):
    """
    NUnit 의 fullname 에서 (테스트 ID, 테스트명) 을 추출한다.

    예: SceneLoadTest.UT001_타이틀씬_로드 → ("UT-001", "타이틀씬 로드")
    """
    method = full_name.split(".")[-1]

    if not method.startswith("UT"):
        return "UNKNOWN", method

    parts = method.split("_", 1)
    number = parts[0][2:]
    name = parts[1].replace("_", " ") if len(parts) > 1 else method

    return f"UT-{number}", name


def _is_ignored(full_name):
    """프레임워크 자동 생성 테스트인지 판별한다."""
    return full_name.startswith(IGNORED_TEST_PREFIXES)


def _parse_test_cases(root):
    """XML 트리에서 개별 테스트 케이스를 추출한다."""
    cases = []

    for node in root.iter("test-case"):
        full_name = node.get("fullname", "")

        if _is_ignored(full_name):
            continue

        test_id, test_name = _split_test_name(full_name)
        passed = node.get("result") == "Passed"

        # fullname 은 "클래스.메서드" 형태이므로 앞부분이 스위트명
        suite = full_name.split(".")[0] if "." in full_name else "Unknown"

        failure = node.find("failure")
        message = ""
        stack_trace = ""

        if failure is not None:
            message_node = failure.find("message")
            stack_node = failure.find("stack-trace")
            message = (message_node.text or "").strip() if message_node is not None else ""
            stack_trace = (stack_node.text or "").strip() if stack_node is not None else ""

        cases.append(TestCase(
            test_id=test_id,
            test_name=test_name,
            passed=passed,
            message=message,
            stack_trace=stack_trace,
            suite=suite,
            duration=float(node.get("duration", 0)),
            full_name=full_name,
        ))

    return cases


def parse_results(xml_path=RESULT_XML):
    """NUnit XML 을 파싱해 집계 결과를 반환한다."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    cases = _parse_test_cases(root)
    failures = [case for case in cases if not case.passed]

    return TestRunResult(
        total=len(cases),
        passed=len(cases) - len(failures),
        failed=len(failures),
        duration=float(root.get("duration", 0)),
        failures=failures,
        cases=cases,
    )


def run_tests():
    """
    Unity CLI 로 테스트를 실행하고 결과를 반환한다.

    Unity 는 테스트 실패 시 종료 코드 2 를 반환하므로
    실패 자체는 예외로 처리하지 않는다.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"[Unity] 테스트 실행 시작")
    print(f"[Unity] 프로젝트: {UNITY_PROJECT_PATH}")

    process = subprocess.run(_build_command(), capture_output=True)
    exit_code = process.returncode

    if exit_code not in (EXIT_SUCCESS, EXIT_TESTS_FAILED):
        raise RuntimeError(
            f"Unity 실행 실패 (종료 코드 {exit_code}). 로그: {UNITY_LOG}"
        )

    if not os.path.exists(RESULT_XML):
        raise RuntimeError(f"테스트 결과 파일이 생성되지 않음: {RESULT_XML}")

    result = parse_results()
    print(f"[Unity] 실행 완료: {result.passed}/{result.total} 통과")

    return result