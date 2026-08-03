#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"

python -m radeonvla.check_env \
  --require-amd \
  --init-genesis \
  --json docs/environment.remote.json

python -m radeonvla.setup_assets
python -m radeonvla.scene --backend amdgpu --steps 50 --save-frames
python -m radeonvla.benchmark --backend amdgpu --steps 200
python -m radeonvla.submission_audit
