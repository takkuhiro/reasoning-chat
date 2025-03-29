FROM python:3.13-slim

WORKDIR /app
ENV PYTHONPATH /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential python3-dev \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . .

EXPOSE 8080

CMD ["chainlit", "run", "/app/src/main.py", "--host", "0.0.0.0", "--port", "8080"]
