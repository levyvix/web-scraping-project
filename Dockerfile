# Multi-stage Docker build for web scraping application
# Builder stage: Install UV and dependencies
FROM python:3.10-slim AS builder

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (production only, no dev dependencies)
RUN uv sync --frozen --no-install-project --no-dev

# Runtime stage: Create optimized production image
FROM python:3.10-slim AS runtime

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Create non-root user for security
RUN groupadd --gid 1000 scraper && \
    useradd --uid 1000 --gid scraper --shell /bin/bash --create-home scraper

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=scraper:scraper /app/.venv /app/.venv

# Copy application code
COPY --chown=scraper:scraper main.py ./
COPY --chown=scraper:scraper healthcheck.py ./
COPY --chown=scraper:scraper utils/ ./utils/

# Create volume mount points with proper permissions
RUN mkdir -p /app/output /app/logs && \
    chown -R scraper:scraper /app/output /app/logs

# Install requests for health check (if not already in dependencies)
RUN /app/.venv/bin/pip install requests

# Switch to non-root user
USER scraper

# Set up volumes for data persistence
VOLUME ["/app/output", "/app/logs"]

# Set container environment variables
ENV CONTAINER_ENV=true \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python healthcheck.py || exit 1

# Set entrypoint and default command
ENTRYPOINT ["python", "main.py"]
CMD []
