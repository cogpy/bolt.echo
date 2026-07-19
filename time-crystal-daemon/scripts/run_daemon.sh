#!/usr/bin/env bash
# Start the Time Crystal Daemon (POSIX)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/../daemon/time_crystal_daemon.py" "$@"
