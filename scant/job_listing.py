from dataclasses import dataclass


@dataclass
class JobListing:
    job_id: int
    posted_on: str
    title: str
    dates: str
