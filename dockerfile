FROM python:3.12.14-bookworm@sha256:dbbe4ceb97851e2e5fa83798b239811f871cb743b259ba3563737349f6bcfaa0

WORKDIR "/var/task"

COPY . .

COPY --from=ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV UV_PYTHON_DOWNLOADS=never
ENV PLAYWRIGHT_BROWSERS_PATH=/var/task/browsers/ms-playwright

RUN uv sync --locked --no-dev --group deploy --no-editable --no-cache && \
	playwright install --with-deps chromium

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

CMD [ "scant.lambda_function.lambda_handler" ]
