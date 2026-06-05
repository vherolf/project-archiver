#!/usr/bin/env bash
set -e

REPO="https://github.com/vherolf/project-archiver.git"
INSTALL_DIR="$HOME/bin/project-archiver"

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating project-archiver..."
    git -C "$INSTALL_DIR" fetch origin
    git -C "$INSTALL_DIR" reset --hard origin/main
else
    echo "Installing project-archiver..."
    mkdir -p "$HOME/bin"
    git clone "$REPO" "$INSTALL_DIR"
fi

# Create or update venv
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"

echo ""
echo "Done."
echo "Run: $INSTALL_DIR/venv/bin/python $INSTALL_DIR/project-archiver.py -s <source> -d <destination>"
echo ""
echo "Add this alias to your shell profile for convenience:"
echo "  alias project-archiver='$INSTALL_DIR/venv/bin/python $INSTALL_DIR/project-archiver.py'"
