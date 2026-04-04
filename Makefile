SHELL := /bin/bash

.PHONY: install run

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
KEDRO := $(VENV)/bin/kedro

install:
	@test -x "$(PYTHON)" || python3 -m venv "$(VENV)"
	"$(PIP)" install -r requirements.txt

run:
	@test -n "$(PIPELINE)" || (echo "Uso: make run PIPELINE=openaire_extract" && exit 1)
	@mkdir -p logs
	@test -x "$(KEDRO)" || (echo "Falta $(KEDRO). Ejecutá: make install" && exit 1)
	"$(KEDRO)" run --tags "$(PIPELINE)" |& tee "logs/$(PIPELINE)_$$(date +%F_%H%M).log"
