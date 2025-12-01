FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for potential future extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project configuration
COPY pyproject.toml /app/

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    pydantic \
    pytest \
    coverage \
    hypothesis \
    httpx

# Copy application code
COPY main.py /app/
COPY tests/ /app/tests/

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
