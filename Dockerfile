FROM python:3.13.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

RUN apt-get update && \
    apt-get -y install unzip && \
    apt-get -y install curl && \
    apt-get -y install gnupg && \
    apt-get -y install wget

RUN curl -sSL -O https://packages.microsoft.com/config/debian/$(grep VERSION_ID /etc/os-release | cut -d '"' -f 2 | cut -d '.' -f 1)/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb

RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18


WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY ingest.py .

ENTRYPOINT ["python", "ingest.py"]