#!/usr/bin/env bash
# End-to-end local smoke: assets -> scene -> expert -> record 1 ep -> validate -> train dry-run
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACKEND="${BACKEND:-cpu}"
python -m radeonvla.pipeline all-smoke \
  --backend "$BACKEND" \
  --episodes 1 \
  --task banana_left \
  --repo-id visiobot/radeonvla_reflex_smoke \
  --dataset-root datasets/radeonvla_reflex_smoke \
  --device cpu \
  --dry-run-train
