# debug/test_jira.py
import sys
sys.path.insert(0, ".")
from utils.device_utils import connect_device
from utils.jira_reporter import JiraReporter

device = connect_device()
reporter = JiraReporter(device)

key = reporter.report_failure(
    test_id="TW-999",
    test_name="Jira 연동 테스트",
    error_short="AssertionError: 연동 확인용",
    error_full="테스트용 traceback",
)
print(f"결과 이슈 키: {key}")