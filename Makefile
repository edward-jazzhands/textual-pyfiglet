.PHONY: run-demo run-dev clean build pyfiglet _pyfiglet

run-demo:
	python -m textual_pyfiglet

run-dev:
	textual run --dev textual_pyfiglet.__main__:PyFigletDemo

clean:
	rm -rf build dist
	find . -name "*.pyc" -delete

build: clean
	poetry build

publish: build
	poetry publish


#-------------------------------------------------------------------------------

# I made sure to preserve the original PyFiglet CLI.
# You can access the original CLI with the following command:
#$ python -m textual_pyfiglet.pyfiglet

# The original PyFiglet CLI has a demo that can be accessed like this (verbatim, with the spaces):
#$ python -m textual_pyfiglet.pyfiglet some text here

# In order to change fonts with the original demo, do this:
#$ python -m textual_pyfiglet.pyfiglet -f small Hello, World!