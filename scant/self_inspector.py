from datetime import datetime, timedelta, timezone
from typing import Literal
import boto3


class SelfInspector:
    def __init__(self, function_name: str) -> None:
        self.__function_name = function_name

    def __get_metric(
        self,
        metric_name: Literal["Errors", "Invocations"],
        now: datetime,
    ) -> float:
        cloudwatch = boto3.client("cloudwatch")
        hour_ago = now - timedelta(hours=1)
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/Lambda",
            MetricName=metric_name,
            Dimensions=[{"Name": "FunctionName", "Value": self.__function_name}],
            StartTime=hour_ago.isoformat(),
            EndTime=now.isoformat(),
            Period=60,
            Statistics=["Sum"],
        )
        if len(response["Datapoints"]) == 0:
            return 0
        return sum(datapoint["Sum"] for datapoint in response["Datapoints"])

    def recently_successful(self) -> bool:
        now = datetime.now(timezone.utc)
        errors = self.__get_metric("Errors", now)
        invocations = self.__get_metric("Invocations", now)
        if invocations == 0:
            return True
        return errors < invocations
