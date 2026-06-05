#!/usr/bin/env bash
set -e

# Locate libmagic on the system
LIBMAGIC=$(ldconfig -p | grep "libmagic\.so" | awk '{print $NF}' | head -1)

if [ -z "$LIBMAGIC" ]; then
    echo "Error: libmagic not found. Install with: sudo apt install libmagic1"
    exit 1
fi

echo "Using libmagic: $LIBMAGIC"

pyinstaller \
    --onefile \
    --name project-archiver \
    --add-binary "$LIBMAGIC:." \
    project-archiver.py

echo ""
echo "Binary ready: dist/project-archiver"
