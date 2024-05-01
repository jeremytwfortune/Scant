from typing import Any
import requests
from scant.constants import BASE_SITE
from scant.job_listing import JobListing


def format_job_listing_as_attachment(job_listing: JobListing) -> dict[str, Any]:
    url = f"{BASE_SITE}/job/{job_listing.job_id}/teacher-job-details"

    return {
        "title": job_listing.title,
        "title_link": url,
        "fields": [
            {"title": "Posted On", "value": job_listing.posted_on, "short": True},
            {"title": "Dates", "value": job_listing.dates, "short": True},
        ],
    }


class SlackNotifier:
    def __init__(self, webhook: str) -> None:
        self.__webhook = webhook

    def send_job_listings(self, job_listings: list[JobListing]) -> None:
        attachments = [format_job_listing_as_attachment(job_listing) for job_listing in job_listings]
        payload = {"text": f"Found {len(job_listings)} new job listings", "attachments": attachments}
        requests.post(self.__webhook, json=payload)

    def send_failure(self) -> None:
        payload = {"text": "Failed to scrape job listings", "channel": "@UQCU37H8F"}

        requests.post(self.__webhook, json=payload)
