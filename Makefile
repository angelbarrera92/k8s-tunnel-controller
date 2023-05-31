.DEFAULT_GOAL: help
SHELL := /bin/bash

PROJECTNAME := $(shell basename "$(PWD)")
CURRENT_DIR := $(shell pwd)

.PHONY: help
all: help
help: Makefile
	@echo
	@echo " Choose a command run in "$(PROJECTNAME)":"
	@echo
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@echo

.PHONY: frigate
## frigate: Run frigate to generate the k8s-tunnel-controller helm chart README.md
frigate:
	@docker run -w /app --rm -v ${CURRENT_DIR}:/app docker.io/library/python:3.10 pip install -r requirements-dev.txt && frigate gen --no-credits -o markdown deployments/kubernetes/helm/k8s-tunnel-controller > deployments/kubernetes/helm/k8s-tunnel-controller/README.md

.PHONY: lint
## lint: Run linters
lint:
	@docker pull ghcr.io/github/super-linter:v4
	@docker run --rm -e RUN_LOCAL=true -e VALIDATE_KUBERNETES_KUBEVAL=false -e VALIDATE_KUBERNETES_KUBECONFORM=false -v ${CURRENT_DIR}:/tmp/lint ghcr.io/github/super-linter:v4

.PHONY: e2e
## e2e: Creates a local kind cluster and runs the e2e tests
e2e:
	@kind delete cluster --name	$(PROJECTNAME)
	@kind create cluster --name $(PROJECTNAME) --image docker.io/kindest/node:v1.26.4
	@kind get kubeconfig --name $(PROJECTNAME) > ${CURRENT_DIR}/kubeconfig
	@export KUBECONFIG=${CURRENT_DIR}/kubeconfig
	@echo "Wait 10 seconds for the cluster to be ready"
	@sleep 10
	@pytest -v tests/e2e.py
	@kind delete cluster --name	$(PROJECTNAME)
	@unset KUBECONFIG
	@rm -rf ${CURRENT_DIR}/kubeconfig

.PHONY: container
## container: Build a local container image
container:
	@docker build -t $(PROJECTNAME):local -f builder/container-images/controller.Dockerfile .
