# Using multi-stage build to seperate build and run environments
# making the final image smaller and more secure.

# ── Stage 1: dependency resolver ─────────────────────────────────────────────

FROM python:3.12-slim@sha256:7026274c107626d7e940e0e5d6730481a4600ae95d5ca7eb532dd4180313fea9 AS builder

WORKDIR /build

RUN pip install --no-cache-dir uv==0.10.2

COPY requirements.txt .

RUN uv pip install \
      --system \
      --no-cache \
      --prefix /install \
      -r requirements.txt

# ── Stage 2: runtime image ────────────────────────────────────────────────────

FROM python:3.12-slim@sha256:7026274c107626d7e940e0e5d6730481a4600ae95d5ca7eb532dd4180313fea9 AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /install/ /usr/local/

COPY app/ ./app/

# Give the appuser permission to use the files
RUN chown -R appuser:appgroup /app

# Switch from "root" (admin) to restricted user
USER appuser

# App listends on port 8000
EXPOSE 8000

# Every 30 seconds, dokcer pings the app to make sure it's still alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]