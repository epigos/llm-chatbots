#!/bin/bash
set -e

PORT=${2:-8000}

case "$1" in
    dev)
        poetry run alembic upgrade head
        poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
        ;;
    serve)
        poetry run alembic upgrade head
        poetry run gunicorn -c ./gunicorn_conf.py app.main:app
        ;;
    manage)
        poetry run python manage.py "$2"
        ;;
    migration)
        alembic revision --autogenerate -m "$2"
        ;;
    upgrade)
        alembic upgrade head
        ;;
    downgrade)
        alembic downgrade base
        ;;
    *)
        exec "$@"
        ;;
esac
