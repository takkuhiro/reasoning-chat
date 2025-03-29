MODE=reasoning-chat
PROJECT_ID?=$(shell echo $$GCP_PROJECT_ID)
REGION?=$(shell echo $$GCP_REGION)
IMAGE_NAME=reasoning-chat
TAG=latest

.PHONY: build
build:
	docker compose build app

.PHONY: push
push:
	docker compose push app

.PHONY: deploy
deploy:
	set -o allexport && source .env && set +o allexport && \
	gcloud run deploy $(MODE) \
		--image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):$(TAG) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--set-env-vars="$(shell cat .env | grep -v '^#' | xargs)"

.PHONY: format
format:
	poetry run black . -l 79
	poetry run isort . --profile black --line-length 79

.PHONY: lint
lint:
	poetry run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py
	poetry run mypy .
	poetry run vulture . --min-confidence 70 --ignore-names token

.PHONY: check
check: format lint
