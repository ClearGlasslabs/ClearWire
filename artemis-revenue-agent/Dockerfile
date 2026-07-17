FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ARTEMIS_HOST=0.0.0.0 \
    ARTEMIS_PORT=8080

RUN useradd --create-home --uid 10001 artemis
WORKDIR /app

COPY pyproject.toml README.md ./
COPY artemis_revenue_agent ./artemis_revenue_agent
RUN pip install --no-cache-dir .

USER artemis
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"

CMD ["artemis-revenue-agent"]
