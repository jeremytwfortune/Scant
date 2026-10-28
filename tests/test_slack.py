from unittest.mock import Mock

import pytest

from scant.constants import BASE_SITE
from scant.job_listing import JobListing
from scant.slack import SlackNotifier, format_job_listing_as_attachment


@pytest.fixture
def post(monkeypatch: pytest.MonkeyPatch) -> Mock:
    post = Mock()
    monkeypatch.setattr("scant.slack.requests.post", post)
    return post


@pytest.fixture
def notifier() -> SlackNotifier:
    return SlackNotifier("https://example.invalid/slack")


def test_attachment_should_include_listing_details_and_link() -> None:
    listing = JobListing(42, "Contract", "Example listing", "November")

    assert format_job_listing_as_attachment(listing) == {
        "title": "Example listing",
        "title_link": f"{BASE_SITE}/job/42/teacher-job-details",
        "fields": [
            {"title": "Job Type", "value": "Contract", "short": True},
            {"title": "Dates", "value": "November", "short": True},
        ],
    }


def test_notifier_should_send_listing_count_and_attachments(notifier: SlackNotifier, post: Mock) -> None:
    listings = [JobListing(42, "Contract", "Example listing", "November")]

    notifier.send_job_listings(listings)

    post.assert_called_once_with(
        "https://example.invalid/slack",
        json={"text": "Found 1 new job listings", "attachments": [format_job_listing_as_attachment(listings[0])]},
    )


def test_notifier_should_send_failure_message(notifier: SlackNotifier, post: Mock) -> None:
    notifier.send_failure()

    post.assert_called_once_with(
        "https://example.invalid/slack", json={"text": "It has been a while since I scraped listings correctly."}
    )
