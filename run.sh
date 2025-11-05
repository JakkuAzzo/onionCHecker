#!/bin/bash

# Simple wrapper script for the onion checker
# Usage: ./run.sh [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/start_onion_checker.sh" "$@"