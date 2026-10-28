from unittest.mock import Mock

import pytest

from scant.authentication import Authentication
from scant.constants import AUTH_SITE, JOB_BOARD, POST_LOGIN_URL
from scant.job_listing import JobListing
from scant.scanner import Scanner


@pytest.fixture
def page() -> Mock:
    return Mock()


@pytest.fixture
def scanner(page: Mock) -> Scanner:
    return Scanner(page)


def test_scanner_should_submit_credentials_and_wait_for_login(scanner: Scanner, page: Mock) -> None:
    email, password, button = Mock(), Mock(), Mock()
    page.locator.side_effect = [email, password, button]

    scanner.login(Authentication("test-user", "test-password", "https://example.invalid/slack"))

    page.goto.assert_called_once_with(AUTH_SITE)
    email.fill.assert_called_once_with("test-user")
    password.fill.assert_called_once_with("test-password")
    button.click.assert_called_once_with()
    page.wait_for_url.assert_called_once_with(f"{POST_LOGIN_URL}/", wait_until="load")


@pytest.mark.parametrize(
    "rows, expected",
    [
        ([], []),
        (
            [
                ["42", "Contract", "November", "Example listing", "Details"],
                ["43", "Contract", "December", "Another listing", "Details", "Extra"],
            ],
            [
                JobListing(42, "Contract", "Example listing", "November"),
                JobListing(43, "Contract", "Another listing", "December"),
            ],
        ),
        (
            [
                ["Header"],
                ["Not an ID", "Type", "Dates", "Title", "Details"],
                ["42", "Contract", "November", "Example listing", "Details"],
            ],
            [JobListing(42, "Contract", "Example listing", "November")],
        ),
    ],
    ids=["empty-table", "valid-listings", "skip-malformed-rows"],
)
def test_scanner_should_parse_valid_job_rows(
    scanner: Scanner, page: Mock, rows: list[list[str]], expected: list[JobListing]
) -> None:
    elements = []
    for values in rows:
        row = Mock()
        row.locator.return_value.all.return_value = [Mock(inner_text=Mock(return_value=value)) for value in values]
        elements.append(row)
    page.locator.return_value.locator.return_value.all.return_value = elements

    assert scanner.get_job_listings() == expected
    page.goto.assert_called_once_with(JOB_BOARD)
