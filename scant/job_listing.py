from dataclasses import dataclass


@dataclass
class JobListing:
    job_id: int
    job_type: str
    title: str
    dates: str
