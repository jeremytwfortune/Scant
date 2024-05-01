from dataclasses import dataclass
import boto3
import os
import json


@dataclass
class Authentication:
    user: str
    password: str
    slack_webhook: str


def get_authentication(secret_name: str | None) -> Authentication:
    if secret_name is None:
        return Authentication(
            user=os.environ.get("SCANT_USER", ""),
            password=os.environ.get("SCANT_PASSWORD", ""),
            slack_webhook=os.environ.get("SCANT_SLACK_WEBHOOK", ""),
        )

    response = boto3.client("secretsmanager").get_secret_value(SecretId=secret_name)
    secret = json.loads(response["SecretString"])

    return Authentication(
        user=secret["user"],
        password=secret["password"],
        slack_webhook=secret["slackWebhook"],
    )
