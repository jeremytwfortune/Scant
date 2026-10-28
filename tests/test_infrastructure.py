from unittest.mock import Mock

import pytest

from scant.authentication import Authentication
from scant.infrastructure import get_infrastructure
from scant.watermark import Watermark


@pytest.fixture
def authentication(monkeypatch: pytest.MonkeyPatch) -> Mock:
    authenticate = Mock(return_value=Authentication("test-user", "test-password", "https://example.invalid/slack"))
    monkeypatch.setattr("scant.infrastructure.get_authentication", authenticate)
    return authenticate


def test_infrastructure_should_load_authentication_and_watermark(authentication: Mock) -> None:
    watermarker = Mock()
    watermarker.get.return_value = Watermark(42)

    infrastructure = get_infrastructure("test-secret", watermarker)

    assert infrastructure.authentication == authentication.return_value
    assert infrastructure.watermark == Watermark(42)
    authentication.assert_called_once_with("test-secret")


def test_infrastructure_should_preserve_cause_when_configuration_fails(authentication: Mock) -> None:
    error = RuntimeError("secret unavailable")
    authentication.side_effect = error

    with pytest.raises(Exception, match="Failed to create infrastructure") as raised:
        get_infrastructure("test-secret", Mock())

    assert raised.value.__cause__ is error
