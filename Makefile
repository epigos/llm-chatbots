.DEFAULT_GOAL = help

#: run linter
lint: format
	poetry lock --check
	poetry run autoflake --check .
	poetry run isort --check-only .
	poetry run black --check .
	poetry run mypy  --show-error-codes .
	poetry run pylint app

#: format all source files
format:
	poetry run autoflake --in-place .
	poetry run isort --atomic .
	poetry run black .

#: run tests
test:
	poetry run pytest -s tests/ -vvv --cov --cov-report term-missing

clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf dist

hooks:
	poetry run pre-commit install --install-hooks

down:
	docker compose down --remove-orphans

db:
	docker compose up -d db

build:
	docker compose build

## migrations: create alembic migration
migrations:
	docker-compose run --rm app migration

## upgrade:   downgrade alembic migrations
upgrade:
	docker compose run --rm app upgrade

## downgrade: downgrade alembic migrations
downgrade:
	docker compose run --rm app downgrade

flush: downgrade upgrade

#: list available make targets
help:
	@grep -B1 -E "^[a-zA-Z0-9_-]+\:([^\=]|$$)" Makefile \
		| grep -v -- -- \
		| sed 'N;s/\n/###/' \
		| sed -n 's/^#: \(.*\)###\(.*\):.*/make \2###    \1/p' \
		| column -t  -s '###' \
		| sort

.PHONY: lint format test clean hooks migrations upgrade downgrade down db build help
