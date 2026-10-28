import json
from unittest.mock import Mock

import pytest

from scant.authentication import Authentication, get_authentication


def test_authentication_should_read_environment_when_no_secret_is_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCANT_USER", "test-user")
    monkeypatch.setenv("SCANT_PASSWORD", "test-password")
    monkeypatch.setenv("SCANT_SLACK_WEBHOOK", "https://example.invalid/slack")

    assert get_authentication(None) == Authentication("test-user", "test-password", "https://example.invalid/slack")


def test_authentication_should_default_to_empty_values(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ["SCANT_USER", "SCANT_PASSWORD", "SCANT_SLACK_WEBHOOK"]:
        monkeypatch.delenv(name, raising=False)

    assert get_authentication(None) == Authentication("", "", "")


def test_authentication_should_read_configured_secret(aws_client: Mock) -> None:
    aws_client.get_secret_value.return_value = {
        "SecretString": json.dumps(
            {"user": "test-user", "password": "test-password", "slackWebhook": "https://example.invalid/slack"}
        )
    }

    assert get_authentication("test-secret") == Authentication(
        "test-user", "test-password", "https://example.invalid/slack"
    )
    aws_client.get_secret_value.assert_called_once_with(SecretId="test-secret")
