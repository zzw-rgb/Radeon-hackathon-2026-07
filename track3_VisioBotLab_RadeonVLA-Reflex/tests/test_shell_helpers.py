from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_latest_pretrained_model_selects_latest_numbered_checkpoint(tmp_path: Path) -> None:
    train_dir = tmp_path / "train"
    older = train_dir / "checkpoints" / "000100" / "pretrained_model"
    latest = train_dir / "checkpoints" / "010000" / "pretrained_model"
    older.mkdir(parents=True)
    latest.mkdir(parents=True)

    command = (
        f"source {ROOT / 'scripts' / 'lib.sh'}; "
        f"latest_pretrained_model {train_dir}"
    )
    result = subprocess.run(
        ["bash", "-c", command],
        check=True,
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.stdout.strip() == str(latest)


def test_latest_pretrained_model_prefers_legacy_last(tmp_path: Path) -> None:
    train_dir = tmp_path / "train"
    legacy = train_dir / "checkpoints" / "last" / "pretrained_model"
    numbered = train_dir / "checkpoints" / "020000" / "pretrained_model"
    legacy.mkdir(parents=True)
    numbered.mkdir(parents=True)

    command = (
        f"source {ROOT / 'scripts' / 'lib.sh'}; "
        f"latest_pretrained_model {train_dir}"
    )
    result = subprocess.run(
        ["bash", "-c", command],
        check=True,
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.stdout.strip() == str(legacy)
