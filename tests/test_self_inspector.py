from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from scant.self_inspector import SelfInspector


@pytest.mark.parametrize(
    "errors, invocations, expected",
    [([], [], True), ([2, 1], [2, 3], True), ([2, 1], [3], False)],
    ids=["no-invocations", "some-successes", "all-failed"],
)
def test_inspector_should_detect_recent_successes(
    aws_client: Mock, errors: list[int], invocations: list[int], expected: bool
) -> None:
    aws_client.get_metric_statistics.side_effect = [
        {"Datapoints": [{"Sum": value} for value in values]} for values in [errors, invocations]
    ]

    assert SelfInspector("test-function").recently_successful() is expected


def test_inspector_should_query_the_last_hour(monkeypatch: pytest.MonkeyPatch, aws_client: Mock) -> None:
    now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    monkeypatch.setattr("scant.self_inspector.datetime", Mock(now=Mock(return_value=now)))
    aws_client.get_metric_statistics.return_value = {"Datapoints": []}

    SelfInspector("test-function").recently_successful()

    assert [call.kwargs for call in aws_client.get_metric_statistics.call_args_list] == [
        {
            "Namespace": "AWS/Lambda",
            "MetricName": metric,
            "Dimensions": [{"Name": "FunctionName", "Value": "test-function"}],
            "StartTime": (now - timedelta(hours=1)).isoformat(),
            "EndTime": now.isoformat(),
            "Period": 60,
            "Statistics": ["Sum"],
        }
        for metric in ["Errors", "Invocations"]
    ]
