#!/bin/sh
cd "$(dirname "$0")"

# Create a virtual environment to run our code
VENV_NAME=".venv"
PYTHON="$VENV_NAME/bin/python"

# Ensure uv is installed
export PATH=$PATH:$HOME/.local/bin
if ! command -v uv >/dev/null 2>&1; then
	if ! command -v curl >/dev/null 2>&1; then
		echo "need curl to install UV. please install curl on this system."
		exit 1
	fi
	curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Optional: Clean up venv on exit (remove if you want to keep venv between runs)
cleanup() {
    if [ -d .venv ]; then
        rm -rf .venv
        echo "Virtual environment cleaned up"
    fi
}
trap cleanup EXIT

# Fix permissions if venv exists (safety net)
if [ -d .venv ]; then
    sudo chown -R "$USER:$USER" .venv
fi

# Install dependencies and create venv if needed
uv sync

# Run the script
exec .venv/bin/python src/main.py "$@"
