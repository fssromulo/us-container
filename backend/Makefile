setup-dev: export-dev build-cached-dev

export-prod:
	@poetry export -f requirements.txt --without-hashes --output requirements.txt

export-dev:
	@poetry export -f requirements.txt --without-hashes --with dev --output requirements-dev.txt

build-dev: export-dev
	@docker-compose -f docker-compose.dev.yml build --no-cache

build-cached-dev:
	@docker-compose -f docker-compose.dev.yml build

bash-dev:
	@docker-compose -f docker-compose.dev.yml run --rm backend bash

run-dev:
	@docker-compose -f docker-compose.dev.yml up

down-dev:
	@docker-compose -f docker-compose.dev.yml down -v

test:
	@docker-compose -f docker-compose.dev.yml run --rm backend bash -c 'pytest tests/test_auth0_management.py'

local-test: export-dev
	@poetry run pytest
