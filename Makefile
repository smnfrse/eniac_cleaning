#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = eniac_cleaning
PYTHON_VERSION = 3.13.5
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	pip install -e .


## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format


## Create environment from environment.yml
.PHONY: create_environment
create_environment:
	conda env create -f environment.yml
	@echo ">>> conda environment created from environment.yml"


## Update environment from environment.yml
.PHONY: update_environment
update-environment:
	conda env update -f environment.yml --prune
	@echo ">>> conda environment updated"


#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Run data cleaning script
.PHONY: data_cleaning
data-cleaning: requirements
	$(PYTHON_INTERPRETER) -m Smn.data_cleaning


## Run data quality checks
.PHONY: data_quality
data-quality: requirements
	$(PYTHON_INTERPRETER) -m Smn.data_quality


## Generate plots
.PHONY: plots
plots: requirements
	$(PYTHON_INTERPRETER) -m Smn.plots


## Run complete data pipeline (cleaning -> quality -> plots)
.PHONY: pipeline
pipeline: data-cleaning data-quality plots
	@echo ">>> Complete data pipeline finished"


## Run data processing only (cleaning -> quality)
.PHONY: data
data: data-cleaning data-quality
	@echo ">>> Data processing finished"


## Clean generated data and figures
.PHONY: clean_outputs
clean-outputs:
	rm -rf data/interim/*
	rm -rf data/processed/*
	rm -rf reports/figures/*
	@echo ">>> Generated outputs cleaned"


## Full clean (including Python cache and outputs)
.PHONY: clean_all
clean-all: clean clean-outputs
	@echo ">>> Full clean completed"


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)