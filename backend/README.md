# Snake Playground Pro - Backend API

Backend API pour Snake Playground Pro, construit avec FastAPI.

## Prérequis

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Gestionnaire de dépendances Python

## Installation

```bash
cd backend
uv sync --extra dev
```

## Lancer le serveur

```bash
uv run uvicorn main:app --reload
```

Ou :

```bash
uv run python main.py
```

Le serveur sera accessible sur :
- API : http://127.0.0.1:8000
- Documentation Swagger : http://127.0.0.1:8000/docs
- Documentation ReDoc : http://127.0.0.1:8000/redoc

## Tests

```bash
uv run pytest
```

Avec couverture de code :

```bash
uv run pytest --cov=app
```

## Structure du projet

```
backend/
├── main.py              # Point d'entrée de l'application
├── app/
│   ├── config.py        # Configuration
│   ├── dependencies.py  # Dépendances FastAPI
│   ├── models/          # Modèles Pydantic
│   ├── routers/         # Routes API
│   └── services/        # Services (auth, database)
└── tests/               # Tests unitaires
```
