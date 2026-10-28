from unittest.mock import MagicMock, Mock

import pytest

from scant import lambda_function
from scant.authentication import Authentication
from scant.infrastructure import Infrastructure
from scant.job_listing import JobListing
from scant.watermark import Watermark


@pytest.fixture
def browser(monkeypatch: pytest.MonkeyPatch) -> Mock:
    playwright = MagicMock()
    monkeypatch.setattr(lambda_function, "sync_playwright", Mock(return_value=playwright))
    return playwright.__enter__.return_value.chromium.launch.return_value


@pytest.fixture
def scanner(monkeypatch: pytest.MonkeyPatch) -> Mock:
    scanner = Mock()
    scanner.get_job_listings.return_value = []
    monkeypatch.setattr(lambda_function, "Scanner", Mock(return_value=scanner))
    return scanner


@pytest.fixture
def watermarker(monkeypatch: pytest.MonkeyPatch) -> Mock:
    watermarker = Mock()
    monkeypatch.setattr(lambda_function, "Watermarker", Mock(return_value=watermarker))
    return watermarker


@pytest.fixture
def inspector(monkeypatch: pytest.MonkeyPatch) -> Mock:
    inspector = Mock()
    monkeypatch.setattr(lambda_function, "SelfInspector", Mock(return_value=inspector))
    return inspector


@pytest.fixture
def infrastructure(monkeypatch: pytest.MonkeyPatch) -> Infrastructure:
    infrastructure = Infrastructure(
        slack=Mock(),
        watermark=Watermark(42),
        authentication=Authentication("test-user", "test-password", "https://example.invalid/slack"),
    )
    monkeypatch.setattr(lambda_function, "get_infrastructure", Mock(return_value=infrastructure))
    return infrastructure


@pytest.fixture(autouse=True)
def handler_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    browser: Mock,
    scanner: Mock,
    watermarker: Mock,
    inspector: Mock,
    infrastructure: Infrastructure,
) -> None:
    monkeypatch.setenv("SCANT_LAMBDA_FUNCTION_NAME", "test-function")
    monkeypatch.delenv("SCANT_AUTHENTICATION_NAME", raising=False)
    monkeypatch.delenv("SCANT_WATERMARK_NAME", raising=False)


def test_handler_should_notify_only_new_listings_and_save_highest_id(
    scanner: Mock, watermarker: Mock, infrastructure: Infrastructure, browser: Mock
) -> None:
    old = JobListing(41, "Contract", "Old listing", "November")
    seen = JobListing(42, "Contract", "Seen listing", "November")
    newest = JobListing(44, "Contract", "Newest listing", "November")
    new = JobListing(43, "Contract", "New listing", "November")
    scanner.get_job_listings.return_value = [old, seen, newest, new]

    assert lambda_function.lambda_handler({}, None) == {"statusCode": 200, "body": "Found 2 new job listings"}
    infrastructure.slack.send_job_listings.assert_called_once_with([newest, new])
    watermarker.set.assert_called_once_with(Watermark(44))
    assert browser.close.called


def test_handler_should_skip_notification_and_watermark_when_nothing_is_new(
    scanner: Mock, watermarker: Mock, infrastructure: Infrastructure
) -> None:
    scanner.get_job_listings.return_value = [JobListing(42, "Contract", "Seen listing", "November")]

    assert lambda_function.lambda_handler({}, None) == {"statusCode": 200, "body": "No new job listings found"}
    infrastructure.slack.send_job_listings.assert_not_called()
    watermarker.set.assert_not_called()


@pytest.mark.parametrize("recently_successful", [True, False])
def test_handler_should_reraise_scraping_failures_and_notify_only_after_sustained_failure(
    scanner: Mock,
    inspector: Mock,
    infrastructure: Infrastructure,
    watermarker: Mock,
    browser: Mock,
    recently_successful: bool,
) -> None:
    error = RuntimeError("scraping failed")
    scanner.get_job_listings.side_effect = error
    inspector.recently_successful.return_value = recently_successful

    with pytest.raises(RuntimeError, match="scraping failed") as raised:
        lambda_function.lambda_handler({}, None)

    assert raised.value is error
    assert infrastructure.slack.send_failure.call_count == (0 if recently_successful else 1)
    watermarker.set.assert_not_called()
    assert browser.close.called


def test_handler_should_preserve_watermark_when_notification_fails(
    scanner: Mock, infrastructure: Infrastructure, watermarker: Mock
) -> None:
    scanner.get_job_listings.return_value = [JobListing(43, "Contract", "New listing", "November")]
    infrastructure.slack.send_job_listings.side_effect = RuntimeError("notification failed")

    with pytest.raises(RuntimeError, match="notification failed"):
        lambda_function.lambda_handler({}, None)

    watermarker.set.assert_not_called()
