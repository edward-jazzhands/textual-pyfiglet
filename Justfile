# Install the package
install:
	uv sync

# Install the package with all extras
install-full:
	uv sync --all-extras

# Run the demo with defined entry command
run:
	uv run textual-pyfiglet

# Run the demo in dev mode
run-dev:
	uv run textual run --dev textual_pyfiglet.demo:TextualPyFigletDemo

# Run the console
console:
	uv run textual console -x EVENT -x SYSTEM

# Run the tmux script (see tmux.sh for details)
tmux:
	chmod +x tmux.sh
	./tmux.sh

# Build the package, run clean first
build: clean
	@echo "Not implemented yet"

# Publish the package, run build first
publish: build
	@echo "Not implemented yet"

# Remove the build and dist directories
clean:
	rm -rf build dist
	find . -name "*.pyc" -delete

# Remove the virtual environment and lock file
del-env:
	rm -rf .venv
	rm -rf uv.lock

#-------------------------------------------------------------------------------

# I made sure to preserve the original PyFiglet CLI.
# You can access the original CLI with the following command:
#$ uv run python -m textual_pyfiglet.pyfiglet

# The original PyFiglet CLI has a demo that can be accessed like this (verbatim, with the spaces):
#$ uv run python -m textual_pyfiglet.pyfiglet some text here

# In order to change fonts with the original demo, do this:
#$ uv run python -m textual_pyfiglet.pyfiglet -f small Hello, World!

