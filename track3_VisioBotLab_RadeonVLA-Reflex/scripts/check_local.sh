#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v conda >/dev/null 2>&1; then
  # Prefer the validated local env when available.
  if conda env list | grep -q 'radeonvla-dev'; then
    RUN=(conda run -n radeonvla-dev --no-capture-output)
  else
    RUN=()
  fi
else
  RUN=()
fi

"${RUN[@]}" python -m radeonvla.check_env --json docs/environment.local.json
"${RUN[@]}" python -m radeonvla.submission_audit
"${RUN[@]}" pytest
"${RUN[@]}" ruff check src tests
