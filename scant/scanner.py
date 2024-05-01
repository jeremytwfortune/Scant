from playwright.sync_api import Page

from scant.authentication import Authentication
from scant.constants import AUTH_SITE, JOB_BOARD, JOB_BOARD_LOAD_DELAY, POST_LOGIN_URL
from scant.job_listing import JobListing


class Scanner:
    def __init__(self, page: Page) -> None:
        self.__page = page

    def login(self, authentication: Authentication) -> None:
        print(f"Logging in as {authentication.user}")
        self.__page.goto(AUTH_SITE)

        email_input = self.__page.locator('input[name="email"]')
        password_input = self.__page.locator('input[name="password"]')
        login_button = self.__page.locator('button[type="submit"]')

        login_button.wait_for()

        email_input.fill(authentication.user)
        password_input.fill(authentication.password)
        login_button.click()

        self.__page.wait_for_url(f"{POST_LOGIN_URL}/", wait_until="load")
        print("Logged in successfully")

    def get_job_listings(self) -> list[JobListing]:
        self.__page.goto(JOB_BOARD)
        self.__page.wait_for_timeout(JOB_BOARD_LOAD_DELAY)

        # title_locator = self.__page.locator("h1")
        # title_locator.wait_for()

        job_listings = []
        rows = self.__page.locator("tbody").locator("tr")

        for row in rows.all():
            columns = row.locator("td")
            job_id, posted_on, title, dates, *_ = columns.all()
            try:
                numeric_job_id = int(job_id.inner_text())
            except ValueError:
                print(f"Skipping row with invalid job ID: {job_id.inner_text()}")
                continue

            job_listing = JobListing(
                job_id=numeric_job_id,
                posted_on=posted_on.inner_text(),
                title=title.inner_text(),
                dates=dates.inner_text(),
            )
            job_listings.append(job_listing)

        return job_listings
