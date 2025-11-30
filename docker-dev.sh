#!/bin/bash

case "$1" in
  up)
    docker-compose up -d
    ;;
  down)
    docker-compose down
    ;;
  logs)
    docker-compose logs -f ${2:-}
    ;;
  restart)
    docker-compose restart ${2:-}
    ;;
  shell-backend)
    docker exec -it snake_backend sh
    ;;
  shell-db)
    docker exec -it snake_postgres psql -U snake_user -d snake_playground
    ;;
  migrate)
    docker exec snake_backend alembic upgrade head
    ;;
  migrate-create)
    docker exec snake_backend alembic revision --autogenerate -m "$2"
    ;;
  reset-db)
    docker-compose down -v
    docker-compose up -d
    ;;
  *)
    echo "Usage: $0 {up|down|logs|restart|shell-backend|shell-db|migrate|migrate-create|reset-db}"
    exit 1
    ;;
esac
