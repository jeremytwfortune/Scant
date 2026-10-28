FROM python:3.14.10-bookworm@sha256:d6bb57cfadfb8917f28e7e6f21640f4943a681edf79fb5ca5b1abccb60c45787

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
