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

lint:
	@docker pull github/super-linter
	@docker run --rm -e RUN_LOCAL=true -v ${CURRENT_DIR}:/tmp/lint github/super-linter
