"""Application configuration."""

import os
from datetime import timedelta

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "snake-playground-pro-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Token expiration delta
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

# CORS Configuration
# Get Codespace name from environment
CODESPACE_NAME = os.getenv("CODESPACE_NAME")
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# Add Codespaces URLs if running in Codespaces
if CODESPACE_NAME:
    CODESPACES_URLS = [
        f"https://{CODESPACE_NAME}-5173.{GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
        f"https://{CODESPACE_NAME}-3000.{GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
        f"https://{CODESPACE_NAME}-8080.{GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}",
    ]
    CORS_ORIGINS.extend(CODESPACES_URLS)
