"""Scene layout for language-conditioned multi-bowl fruit sorting.

Layout choices:
- five pickable fruits (banana, lemon, plum, apple, orange);
- four destination bowls: left/right neutral + blue left/right;
- world + wrist cameras for policy observations, plus a cosmetic video camera.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from radeonvla.paths import ASSETS_DIR, ROBOT_DIR, YCB_DIR
from radeonvla.protocol import BOWL_YCB, FRUIT_YCB

TABLE_TOP_Z = 0.75
TABLE_CENTER = (0.35, 0.0)
TABLE_TOP_SIZE = (1.20, 0.80, 0.05)
TABLE_LEG_SIZE = (0.06, 0.06)
TABLE_LEG_INSET = 0.10
TABLE_COLOR = (0.62, 0.47, 0.35, 1.0)
TABLE_LEG_COLOR = (0.47, 0.35, 0.24, 1.0)

FRANKA_POS = (-0.10, 0.0, TABLE_TOP_Z)
FRANKA_EULER = (0.0, 0.0, 0.0)
FRANKA_QPOS = (0.0, -0.3, 0.0, -2.0, 0.0, 1.7, 0.79, 0.04, 0.04)
FRANKA_KP = (4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100)
FRANKA_KV = (450, 450, 350, 350, 200, 200, 200, 10, 10)
FRANKA_FORCE_MIN = (-87, -87, -87, -87, -12, -12, -12, -100, -100)
FRANKA_FORCE_MAX = (87, 87, 87, 87, 12, 12, 12, 100, 100)

# Reachable workspace clamp for pose jitter (slightly wider for denser clutter).
REACH_X = (0.28, 0.50)
REACH_Y = (-0.28, 0.28)

# Solid blue for the two blue bowls (RGBA).
BLUE_BOWL_COLOR = (0.12, 0.38, 0.88, 1.0)
# Slight off-white for neutral bowls so they read as non-blue under DR off.
NEUTRAL_BOWL_COLOR = (0.82, 0.80, 0.76, 1.0)

# Entity layout: five fruits + four bowls.
OBJECT_LAYOUT: dict[str, dict] = {
    # -- fruits (front / mid table, spaced for parallel-jaw grasps) --
    "banana": {
        "ycb": FRUIT_YCB["banana"],
        "pos": (0.30, 0.18, 0.0),
        "euler": (0.0, 0.0, 35.0),
        "kind": "fruit",
    },
    "lemon": {
        "ycb": FRUIT_YCB["lemon"],
        "pos": (0.33, 0.02, 0.0),
        "euler": (0.0, 0.0, 0.0),
        "friction": 1.0,
        "kind": "fruit",
    },
    "plum": {
        "ycb": FRUIT_YCB["plum"],
        "pos": (0.36, -0.14, 0.0),
        "euler": (0.0, 0.0, 0.0),
        "friction": 1.0,
        "kind": "fruit",
    },
    "apple": {
        "ycb": FRUIT_YCB["apple"],
        "pos": (0.40, 0.12, 0.0),
        "euler": (0.0, 0.0, 10.0),
        "friction": 1.0,
        "kind": "fruit",
    },
    "orange": {
        "ycb": FRUIT_YCB["orange"],
        "pos": (0.41, -0.06, 0.0),
        "euler": (0.0, 0.0, 0.0),
        "friction": 1.0,
        "kind": "fruit",
    },
    # -- containers (far +x edge of the table) --
    "left_bowl": {
        "ycb": BOWL_YCB,
        "pos": (0.52, 0.24, 0.0),
        "euler": (0.0, 0.0, 0.0),
        "kind": "container",
        "color": NEUTRAL_BOWL_COLOR,
    },
    "right_bowl": {
        "ycb": BOWL_YCB,
        "pos": (0.52, -0.24, 0.0),
        "euler": (0.0, 0.0, 0.0),
        "kind": "container",
        "color": NEUTRAL_BOWL_COLOR,
    },
    "blue_left_bowl": {
        "ycb": BOWL_YCB,
        "pos": (0.56, 0.10, 0.0),
        "euler": (0.0, 0.0, 0.0),
        "kind": "container",
        "color": BLUE_BOWL_COLOR,
    },
    "blue_right_bowl": {
        "ycb": BOWL_YCB,
        "pos": (0.56, -0.10, 0.0),
        "euler": (0.0, 0.0, 0.0),
        "kind": "container",
        "color": BLUE_BOWL_COLOR,
    },
}

# HSV appearance priors for optional domain randomization (plausible colors only).
DR_APPEARANCE_PRIORS: dict[str, dict[str, tuple[float, float]]] = {
    "banana": {"hue": (48.0, 68.0), "sat": (0.55, 0.95), "val": (0.60, 0.90)},
    "lemon": {"hue": (48.0, 62.0), "sat": (0.60, 1.00), "val": (0.70, 0.95)},
    "plum": {"hue": (300.0, 345.0), "sat": (0.35, 0.80), "val": (0.25, 0.55)},
    "apple": {"hue": (0.0, 25.0), "sat": (0.55, 0.95), "val": (0.40, 0.85)},
    "orange": {"hue": (20.0, 40.0), "sat": (0.70, 1.00), "val": (0.55, 0.95)},
    "left_bowl": {"hue": (20.0, 50.0), "sat": (0.00, 0.25), "val": (0.55, 0.90)},
    "right_bowl": {"hue": (20.0, 50.0), "sat": (0.00, 0.25), "val": (0.55, 0.90)},
    # Blue bowls stay in a blue band even under DR.
    "blue_left_bowl": {"hue": (200.0, 240.0), "sat": (0.55, 0.95), "val": (0.40, 0.85)},
    "blue_right_bowl": {"hue": (200.0, 240.0), "sat": (0.55, 0.95), "val": (0.40, 0.85)},
}

# Cameras: policy uses world + wrist at dataset resolution; video is cosmetic only.
WORLD_CAM_RES = (320, 240)
WORLD_CAM_POS = (
    TABLE_CENTER[0] + TABLE_TOP_SIZE[0] / 2,
    TABLE_CENTER[1] - TABLE_TOP_SIZE[1] / 2,
    TABLE_TOP_Z + 1.0,
)
WORLD_CAM_LOOKAT = (TABLE_CENTER[0], TABLE_CENTER[1], TABLE_TOP_Z)
WORLD_CAM_FOV = 42

WRIST_CAM_RES = (320, 240)
WRIST_CAM_FOV = 42
WRIST_CAM_LINK = "hand"
WRIST_CAM_OFFSET_POS = (0.05, 0.0, -0.03)
WRIST_CAM_OFFSET_EULER = (180.0, 0.0, 0.0)
WRIST_CAM_NEAR = 0.01
WRIST_CAM_FAR = 20.0

VIDEO_CAM_RES = (640, 360)
VIDEO_CAM_POS = (
    TABLE_CENTER[0],
    TABLE_CENTER[1] - 1.0,
    TABLE_TOP_Z + 0.45,
)
VIDEO_CAM_LOOKAT = (TABLE_CENTER[0], TABLE_CENTER[1], TABLE_TOP_Z + 0.05)
VIDEO_CAM_FOV = 42


@dataclass(frozen=True, slots=True)
class MeshAsset:
    entity_name: str
    ycb_name: str
    mesh_path: Path
    collision_path: Path
    rest_z_offset: float
    radius_xy: float


def _mesh_geometry(mesh_path: Path) -> tuple[float, float]:
    import trimesh

    mesh = trimesh.load(mesh_path, force="mesh")
    lower, upper = mesh.bounds
    rest_z_offset = float(-lower[2])
    dx = float(upper[0] - lower[0])
    dy = float(upper[1] - lower[1])
    radius_xy = 0.5 * float((dx**2 + dy**2) ** 0.5)
    return rest_z_offset, radius_xy


def get_mesh_assets() -> dict[str, MeshAsset]:
    assets: dict[str, MeshAsset] = {}
    for entity_name, layout in OBJECT_LAYOUT.items():
        ycb_name = layout["ycb"]
        mesh_path = YCB_DIR / ycb_name / "textured.obj"
        collision_path = YCB_DIR / ycb_name / "collision.ply"
        if not mesh_path.is_file():
            raise FileNotFoundError(
                f"Missing mesh for {entity_name}: {mesh_path}. Run: python -m radeonvla.setup_assets"
            )
        rest_z, radius = _mesh_geometry(mesh_path)
        assets[entity_name] = MeshAsset(
            entity_name=entity_name,
            ycb_name=ycb_name,
            mesh_path=mesh_path,
            collision_path=collision_path,
            rest_z_offset=rest_z,
            radius_xy=radius,
        )
    return assets


def franka_mjcf_path() -> Path:
    path = ROBOT_DIR / "panda.xml"
    if not path.is_file():
        raise FileNotFoundError(f"Missing Franka MJCF at {path}. Run: python -m radeonvla.setup_assets")
    return path


def assets_root() -> Path:
    return ASSETS_DIR
