# Install the package
install:
	uv sync

# Run the demo with defined entry command
run:
	uv run textual-pyfiglet

# Run the demo in dev mode
run-dev:
	uv run textual run --dev textual_pyfiglet.demo:TextualPyFigletDemo

# Run the script to generate the fonts list.
make-list:
	uv run scripts/make_fonts_list.py

# Run the console
console:
	uv run textual console -x EVENT -x SYSTEM


# Runs ruff, exits with 0 if no issues are found
lint:
  @uv run ruff check src || (echo "Ruff found issues. Please address them." && exit 1)

# Runs mypy and basedpyright on src/, exits with 0 if no issues are found
typecheck:
  @uv run mypy src || (echo "Mypy found issues. Please address them." && exit 1)
  @uv run basedpyright src || (echo "BasedPyright found issues. Please address them." && exit 1)

# Runs typecheckers on tests/, exits with 0 if no issues are found
typecheck-tests:
  @uv run mypy tests || (echo "Mypy found issues in tests. Please address them." && exit 1)
  @uv run basedpyright tests || (echo "BasedPyright found issues in tests. Please address them." && exit 1)

# Runs black on src/
format:
  @uv run black src

# Runs pytest, exits with 0 if no issues are found
test:
  @uv run pytest tests -svvv

# Run the Nox testing suite for comprehensive testing
nox:
  nox

# NOTE: Nox must be installed as a global tool, it can't be installed
# as a dev dependency because it manages virtual environments.
# I install nox using UV (`uv tool install nox`). It looks for the noxfile.py.

# Remove build/dist directories and pyc files
clean:
  rm -rf build dist
  find . -name "*.pyc" -delete

# Remove tool caches
clean-caches:
  rm -rf .mypy_cache
  rm -rf .ruff_cache
  rm -rf .nox

# Remove the virtual environment and lock file
del-env:
  rm -rf .venv
  rm -rf uv.lock

# Delete environment, caches, and build artifacts
nuke: clean clean-caches del-env
  @echo "All build artifacts and caches have been removed."

# Runs nuke then install
reset: nuke install
  @echo "Environment reset."

# Run the .github/scripts files and push the tags
release: sync-tags
  bash .github/scripts/release.sh && \
  git push --tags

# git push --tags does not push commits to your main branch (or any other branch). It only 
# uploads the "tag objects"—which are essentially just small pointers that say, "This 
# specific commit hash has the name v1.0."

# Because a tag is just metadata sitting "on top" of a commit that usually already exists 
# on the server, pushing a tag doesn't change the branch itself. And so the push request
# is not blocked by Github's branch protection rules even if its configured to block 
# pushes to the main branch.

# Syncs the tags from origin to local
sync-tags:
  git fetch --prune origin "+refs/tags/*:refs/tags/*"

sync-ci:
  curl -fsSL https://raw.githubusercontent.com/edward-jazzhands/ci-shared-python/main/sync.sh | bash