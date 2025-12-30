#!/bin/bash
# Extract version from git tag
VERSION=$(git describe --tags --always 2>/dev/null)

if [ -z "$VERSION" ]; then
    VERSION="0.0.0-dev"
else
    # Remove 'v' prefix if present
    VERSION="${VERSION#v}"
fi

echo "SBCMAN_VERSION $VERSION"
