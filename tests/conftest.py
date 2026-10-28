from unittest.mock import Mock

import boto3
import pytest
import requests


@pytest.fixture(autouse=True)
def block_external_services(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(boto3, "client", Mock(side_effect=AssertionError("AWS client was not mocked")))
    monkeypatch.setattr(
        requests.sessions.Session, "request", Mock(side_effect=AssertionError("HTTP request was not mocked"))
    )


@pytest.fixture
def aws_client(monkeypatch: pytest.MonkeyPatch) -> Mock:
    client = Mock()
    monkeypatch.setattr(boto3, "client", Mock(return_value=client))
    return client
