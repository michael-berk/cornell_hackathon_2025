.SHELLFLAGS := -ec
.PHONY: test lint format check

SRC_DIR := src
TESTS_DIR := tests

export PYTHONPATH := $(shell pwd)

test:
	python -m pytest $(TESTS_DIR)

lint:
	ruff check $(SRC_DIR)

format:
	ruff format $(SRC_DIR)
	ruff check $(SRC_DIR) --fix

check: test lint
