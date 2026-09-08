SHELL := /bin/bash

IMAGE_NAME       ?= basic-ai-agent
JFROG_REGISTRY   ?= $(JFROG_DOCKER_REGISTRY)
SHA              := $(shell git rev-parse --short HEAD)
BRANCH           := $(shell git rev-parse --abbrev-ref HEAD)

.PHONY: help install lint test build push pr tag promote

help:
	@echo "make install          install dev dependencies"
	@echo "make lint             run ruff"
	@echo "make test             run pytest"
	@echo "make build            docker build, tagged with current git sha"
	@echo "make push             docker push the sha-tagged image to JFrog"
	@echo "make pr               open a PR from the current branch into main (gh CLI)"
	@echo "make tag VERSION=x.y.z   create + push annotated tag vx.y.z (triggers release.yml)"
	@echo "make promote ENV=staging|production VERSION=vx.y.z   run the approval-gated promote workflow"

install:
	pip install -r requirements-dev.txt

lint:
	ruff check .

test:
	pytest tests/ -q

build:
	docker build -t $(IMAGE_NAME):sha-$(SHA) .

push: build
	@test -n "$(JFROG_REGISTRY)" || (echo "JFROG_DOCKER_REGISTRY is not set" && exit 1)
	docker tag $(IMAGE_NAME):sha-$(SHA) $(JFROG_REGISTRY)/$(IMAGE_NAME):sha-$(SHA)
	docker push $(JFROG_REGISTRY)/$(IMAGE_NAME):sha-$(SHA)

pr:
	@test "$(BRANCH)" != "main" || (echo "refusing to open a PR from main" && exit 1)
	git push -u origin $(BRANCH)
	gh pr create --fill --base main --head $(BRANCH)

tag:
	@test -n "$(VERSION)" || (echo "usage: make tag VERSION=1.2.3" && exit 1)
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)
	@echo "Pushed tag v$(VERSION) -- this triggers the release workflow (build promotion + apps-repo PR to dev)."

promote:
	@test -n "$(ENV)" || (echo "usage: make promote ENV=staging|production VERSION=vx.y.z" && exit 1)
	@test -n "$(VERSION)" || (echo "usage: make promote ENV=staging|production VERSION=vx.y.z" && exit 1)
	gh workflow run promote.yml -f environment=$(ENV) -f version=$(VERSION)
	@echo "Requested promotion of $(VERSION) to $(ENV) -- requires approval on the '$(ENV)' GitHub Environment."
