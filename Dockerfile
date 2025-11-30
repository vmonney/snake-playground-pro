# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
COPY frontend/bun.lockb ./
RUN npm ci --prefer-offline --no-audit

COPY frontend/ ./

# Use relative path for same-origin API calls
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build
RUN ls -la /app/frontend/dist

# ============================================
# Stage 2: Production Runtime
# ============================================
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install UV and Python dependencies
RUN pip install --no-cache-dir uv
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy backend code
COPY backend/ ./

# Create scripts directory
RUN mkdir -p /app/scripts
COPY backend/scripts/start-backend.sh /app/scripts/start-backend.sh
RUN chmod +x /app/scripts/start-backend.sh

# Copy frontend build from stage 1
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html
RUN ls -la /usr/share/nginx/html

# Copy configurations
COPY combined.nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default
COPY combined.supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directory
RUN mkdir -p /var/log/supervisor

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
