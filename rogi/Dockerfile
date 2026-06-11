FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY rogi/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium --with-deps

COPY rogi/ ./rogi/

EXPOSE 8000

CMD ["uvicorn", "rogi.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
