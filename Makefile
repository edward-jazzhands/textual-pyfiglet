.DEFAULT_GOAL := help

help:
	@echo "Usage:"
	@echo "  make install          Install the package"
	@echo "  make install-full     Install the package with all extras"
	@echo "  make activate         Activate the virtual environment"
	@echo "  make run              Run the demo with defined entry command (requires install)"
	@echo "  make run-demo         Run the demo with python -m (works with poetry's --no-root)"
	@echo "  make run-dev          Run the demo in dev mode"
	@echo "  make clean            Delete dist and pycache files"
	@echo "  make build            Build the package, cleans first"
	@echo "  make publish          Publish the package, builds first"
	@echo "  make del-env          Delete the virtual environment"

.PHONY: install install-full run-demo run-dev clean build publish

install: del-env
	poetry install

install-full: del-env
	poetry install --all-extras

activate:
	poetry shell

# This is set as entry script and assumes package is installed:
# note that this actually points to the original source package.
# poetry uses symbolic links for the current project
run:
	textual-pyfiglet

# this works without installing the package:
run-demo:
	python -m textual_pyfiglet

# dev mode sends messages to textual debug console
run-dev:
	textual run --dev textual_pyfiglet.__main__:PyFigletDemo

clean:
	rm -rf build dist
	find . -name "*.pyc" -delete

build: clean
	poetry build

publish: build
	poetry publish

del-env:
	rm -rf .venv

#-------------------------------------------------------------------------------

# I made sure to preserve the original PyFiglet CLI.
# You can access the original CLI with the following command:
#$ python -m textual_pyfiglet.pyfiglet

# The original PyFiglet CLI has a demo that can be accessed like this (verbatim, with the spaces):
#$ python -m textual_pyfiglet.pyfiglet some text here

# In order to change fonts with the original demo, do this:
#$ python -m textual_pyfiglet.pyfiglet -f small Hello, World!