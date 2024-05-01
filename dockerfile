FROM python:3.12

WORKDIR "/var/task"

COPY . .

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="${PATH}:/root/.local/bin"
ENV PLAYWRIGHT_BROWSERS_PATH=/var/task/browsers/ms-playwright

RUN poetry config virtualenvs.create false && \
	poetry install --no-interaction --with=main,deploy && \
	playwright install --with-deps chromium

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

CMD [ "scant.lambda_function.lambda_handler" ]
