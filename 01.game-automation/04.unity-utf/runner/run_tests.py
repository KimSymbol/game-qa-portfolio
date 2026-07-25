# 역할: Unity 테스트 실행부터 리포팅까지 전체 파이프라인 실행

import sys

sys.path.insert(0, ".")

from utils.bug_reporter import BugReporter
from utils.jira_reporter import JiraReporter
from utils.slack_notifier import SlackNotifier
from utils.unity_runner import run_tests
from utils.allure_reporter import generate as generate_allure


# ── 1. 변수 선언부 ──────────────────────────────────

# 테스트 실패 시 반환할 종료 코드 (CI 가 실패로 인식하도록)
EXIT_FAILURE = 1
EXIT_SUCCESS = 0


# ── 2. 함수 선언부 ──────────────────────────────────

def _report_to_jira(failures):
    """
    실패한 테스트를 Jira 에 보고하고 {테스트ID: 이슈키} 를 반환한다.

    Jira 전송이 실패해도 파이프라인은 계속 진행한다.
    """
    jira_keys = {}

    try:
        reporter = JiraReporter()
    except Exception as error:
        print(f"[Jira] 초기화 실패: {error}")
        return jira_keys

    for failure in failures:
        try:
            issue_key = reporter.report_failure(
                failure.test_id,
                failure.test_name,
                failure.message,
                failure.stack_trace,
            )
            if issue_key:
                jira_keys[failure.test_id] = issue_key
        except Exception as error:
            print(f"[Jira] {failure.test_id} 전송 중 오류: {error}")

    return jira_keys


def _report_to_file(failures):
    """실패한 테스트를 CSV/XLSX 버그 리포트로 기록한다."""
    if not failures:
        return

    try:
        reporter = BugReporter()

        for failure in failures:
            reporter.add_bug(failure.test_id, failure.test_name)

        for file_type, path in reporter.get_paths().items():
            if path:
                print(f"[BugReport] {file_type.upper()}: {path}")

    except Exception as error:
        print(f"[BugReport] 기록 중 오류: {error}")


def _notify_slack(result, jira_keys):
    """테스트 결과 요약을 Slack 으로 전송한다."""
    try:
        SlackNotifier().send_summary(result, jira_keys)
    except Exception as error:
        print(f"[Slack] 전송 중 오류: {error}")


def _print_summary(result):
    """콘솔에 결과 요약을 출력한다."""
    print()
    print("=" * 50)
    print(f"전체: {result.total}  성공: {result.passed}  실패: {result.failed}")
    print(f"소요 시간: {result.duration:.1f}초")

    for failure in result.failures:
        print(f"  ❌ {failure.test_id} {failure.test_name}")

    print("=" * 50)

def _generate_allure(result):
    """Allure 리포트 결과 파일을 생성한다."""
    try:
        generate_allure(result)
    except Exception as error:
        print(f"[Allure] 생성 중 오류: {error}")


def main():
    """Unity 테스트를 실행하고 결과에 따라 리포팅한다."""
    result = run_tests()

    jira_keys = _report_to_jira(result.failures) if result.failures else {}
    _report_to_file(result.failures)
    _generate_allure(result)  
    _notify_slack(result, jira_keys)
    _print_summary(result)

    return EXIT_FAILURE if result.failed else EXIT_SUCCESS


# ── 3. 메인 실행부 ──────────────────────────────────

if __name__ == "__main__":
    sys.exit(main())