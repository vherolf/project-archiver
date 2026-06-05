#!/usr/bin/env bash
set -e

REPO="https://github.com/vherolf/project-archiver.git"
INSTALL_DIR="$HOME/.local/share/project-archiver"
BIN_DIR="$HOME/.local/bin"
BIN="$BIN_DIR/project-archiver"

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating project-archiver..."
    git -C "$INSTALL_DIR" pull
else
    echo "Installing project-archiver..."
    git clone "$REPO" "$INSTALL_DIR"
fi

# Create or update venv
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"

# Write launcher to ~/.local/bin
mkdir -p "$BIN_DIR"
cat > "$BIN" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/project-archiver.py" "\$@"
EOF
chmod +x "$BIN"

echo ""
echo "Done. Run: project-archiver -s <source> -d <destination>"

# Warn if ~/.local/bin is not in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "Note: add this to your shell profile to use it anywhere:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
