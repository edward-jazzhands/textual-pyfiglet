#!/usr/bin/env bash

# The -e flag makes bash exit immediately if any command fails, rather than continuing to 
# execute the rest of the script.
# The -u flag treats unset variables as errors instead of silently expanding them to empty 
# strings, which catches a lot of subtle bugs. 
# The -o pipefail flag makes a pipeline (like cmd1 | cmd2) fail if any command in it fails, 
# not just the last one — by default bash only checks the exit code of the last command in a pipe.
# Together these form the standard "strict mode" to make bash scripts fail fast.
set -euo pipefail

# Step 1 of the 'release' workflow. (`just release`).
# We must be on main and it must be up to date with origin/main for the process
# to continue.
# This is because it creates a new tag based on the version in pyproject.toml,
# and then pushes the tag to GitHub. Tags are metadata that go over the top of
# branches and commits, so they're not blocked by branch protection rules.
# That's why it's important to make sure you're on main and it's up to date.

# If we're not on main or it's not up to date with origin/main, problems could
# occur, such as:
# - The 'version' in pyproject.toml doesn't match what's in the online main
#   branch on Github
# - You push a tag that points to a commit that Github hasn't seen yet,

# It's best to ensure you can't do any of these things by mistake, because it's
# a pain in the ass to fix them if you do.

# Check if on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
	echo "Error: You are not on the main branch. Please switch to main."
	exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
	echo "Error: There are uncommitted changes. Please commit or stash them."
	exit 1
fi

# Fetch latest changes from remote
git fetch

# Check if local main is up to date with origin/main
if ! git rev-parse origin/main > /dev/null 2>&1; then
	echo "Error: Remote branch origin/main does not exist. Please set up a remote tracking branch."
	exit 1
fi
LOCAL_HASH=$(git rev-parse main)
REMOTE_HASH=$(git rev-parse origin/main)
if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
	echo "Error: Your local main branch is not up to date with origin/main. Please pull the latest changes."
	exit 1
fi


# grep '^version' finds lines starting with 'version' (^ anchors to line start,
# preventing false matches on keys like 'requires-python').
# head -1 takes only the first line (just to be safe).
# sed then strips everything except the version string itself, using a capture
# group \(.*\) to grab what's between the quotes, and \1 to output just that.
version=$(grep '^version' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
tag="v${version}"

echo "Found version ${version}. Creating tag: ${tag}"

if git tag "$tag"; then
    echo "Successfully created tag '${tag}'."
else
    echo "Error: Could not create tag '${tag}'."
    exit 1
fi