#!/bin/bash

set -e
set -x

# Automatically update changelog with new version number
VERSION="$(./setup.py --version)"
dch -b -v "${VERSION}" "Automatic build"

# Build package ignoring the modified changelog
gbp buildpackage -us -uc --git-ignore-new

# If the build was successfull, rebase a new ubuntu-ppa branch and push it for Launchpad to consume
git checkout -B ubuntu-ppa
git add debian/changelog
git commit -m "Automatic build"

# @TODO: this would require SSH keys/permissions from inside the Docker container or Travis-CI runner,
# thus will not work...
git push --force --set-upstream origin ubuntu-ppa

# Move back to previous branch and reset debian/changelog
git checkout -
git checkout debian/changelog
