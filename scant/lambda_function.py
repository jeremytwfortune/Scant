import os
from typing import Any
from playwright.sync_api import sync_playwright

from scant.infrastructure import get_infrastructure
from scant.scanner import Scanner
from scant.watermark import Watermark, Watermarker


def lambda_handler(event, context) -> Any:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        scanner = Scanner(page)
        watermarker = Watermarker(os.environ.get("SCANT_WATERMARK_NAME"))

        infrastructure = get_infrastructure(os.environ.get("SCANT_AUTHENTICATION_NAME"), watermarker)

        try:
            scanner.login(infrastructure.authentication)
            job_listings = scanner.get_job_listings()
            new_job_listings = [
                job_listing
                for job_listing in job_listings
                if job_listing.job_id > infrastructure.watermark.last_known_id
            ]

            browser.close()

            if len(new_job_listings) == 0:
                print("No new job listings found")
                return {"statusCode": 200, "body": "No new job listings found"}

            infrastructure.slack.send_job_listings(new_job_listings)

            max_job_id = max(job_listing.job_id for job_listing in new_job_listings)
            watermarker.set(Watermark(max_job_id))

            return {"statusCode": 200, "body": f"Found {len(new_job_listings)} new job listings"}

        except Exception as error:
            infrastructure.slack.send_failure()
            raise error

        finally:
            browser.close()


if __name__ == "__main__":
    lambda_handler(None, None)
