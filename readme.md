# Scant

Scans for new contracted job listings and posts to our family's Slack.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then set up Python 3.14 and the development dependencies:

```text
uv sync --locked --python 3.14
uv run playwright install chromium
```

Run development tools with `uv run`, for example `uv run black --check .`.
The Docker build installs the locked dependencies, including the `deploy` group, and Chromium.
