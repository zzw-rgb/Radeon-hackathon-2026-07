"""Populate bundled simulation assets from known local sources when missing.

Assets are not committed as large binaries. This helper is idempotent: if the
required files already exist under ``assets/``, it does nothing. Otherwise it
copies from well-known development locations (reference demo, Genesis install).
"""

from __future__ import annotations

import argparse
import importlib
import shutil
from pathlib import Path

from radeonvla.paths import ASSETS_DIR, PROJECT_ROOT, ROBOT_DIR, YCB_DIR
from radeonvla.protocol import BOWL_YCB, FRUIT_YCB

REQUIRED_YCB = tuple(sorted({*FRUIT_YCB.values(), BOWL_YCB}))
REQUIRED_OBJECT_FILES = ("textured.obj", "collision.ply")
ROBOT_REQUIRED = "panda.xml"


def _have_object(directory: Path) -> bool:
    return directory.is_dir() and all((directory / name).is_file() for name in REQUIRED_OBJECT_FILES)


def _copy_tree(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _candidate_ycb_roots() -> list[Path]:
    roots: list[Path] = []
    # Sibling development workspaces.
    for relative in (
        Path("../../references/franka_fruit_pick_demo/assets/ycb"),
        Path("../../../references/franka_fruit_pick_demo/assets/ycb"),
        Path("../../RadeonVLA-Reflex/assets/ycb"),
    ):
        roots.append((PROJECT_ROOT / relative).resolve())
    # Explicit override.
    env = Path.home() / ".cache" / "radeonvla" / "ycb"
    roots.append(env)
    return roots


def _candidate_franka_roots() -> list[Path]:
    roots: list[Path] = []
    for relative in (
        Path("../../references/franka_fruit_pick_demo/assets/robots/franka"),
        Path("../../../references/franka_fruit_pick_demo/assets/robots/franka"),
        Path("../../references/genesis-world/genesis/assets/xml/franka_emika_panda"),
    ):
        roots.append((PROJECT_ROOT / relative).resolve())
    try:
        genesis = importlib.import_module("genesis")
        genesis_root = Path(genesis.__file__).resolve().parent
        roots.append(genesis_root / "assets" / "xml" / "franka_emika_panda")
    except Exception:
        pass
    return roots


def setup_assets(*, force: bool = False) -> Path:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []

    ycb_roots = [root for root in _candidate_ycb_roots() if root.is_dir()]
    for name in REQUIRED_YCB:
        dst = YCB_DIR / name
        if _have_object(dst) and not force:
            continue
        src = next((root / name for root in ycb_roots if _have_object(root / name)), None)
        if src is None:
            missing.append(f"ycb/{name}")
            continue
        _copy_tree(src, dst)
        print(f"[assets] copied ycb/{name} <- {src}")

    robot_ready = (ROBOT_DIR / ROBOT_REQUIRED).is_file() and not force
    if not robot_ready:
        src = next((root for root in _candidate_franka_roots() if (root / ROBOT_REQUIRED).is_file()), None)
        if src is None:
            missing.append("robots/franka")
        else:
            _copy_tree(src, ROBOT_DIR)
            print(f"[assets] copied robots/franka <- {src}")

    if missing:
        hint = (
            "Missing assets and no local source found:\n  "
            + "\n  ".join(missing)
            + "\nPlace YCB object folders under assets/ycb/<name>/{textured.obj,collision.ply}\n"
            "and Franka MJCF under assets/robots/franka/panda.xml, then re-run."
        )
        raise FileNotFoundError(hint)

    print(f"[assets] ready at {ASSETS_DIR}")
    return ASSETS_DIR


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-copy assets even if present.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_assets(force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
