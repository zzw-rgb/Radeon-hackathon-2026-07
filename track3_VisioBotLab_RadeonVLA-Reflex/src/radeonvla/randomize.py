"""Per-episode scene randomization for dual-bowl sorting tasks."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from radeonvla.scene_config import (
    FRANKA_QPOS,
    OBJECT_LAYOUT,
    REACH_X,
    REACH_Y,
    TABLE_TOP_Z,
    WORLD_CAM_LOOKAT,
    WORLD_CAM_POS,
    get_mesh_assets,
)
from radeonvla.tasks import TASKS, TaskSpec, get_task

OVERLAP_MARGIN = 0.02
FRUIT_NAMES = ("banana", "lemon", "plum", "apple", "orange")
CONTAINER_NAMES = ("left_bowl", "right_bowl", "blue_left_bowl", "blue_right_bowl")


@dataclass
class RuntimeDR:
    """Runtime (per-episode) physics / camera extrinsics randomization."""

    enabled: bool = False
    friction_ratio_range: tuple[float, float] = (0.7, 1.3)
    mass_ratio_range: tuple[float, float] = (0.8, 1.2)
    cam_pos_jitter: float = 0.0
    cam_lookat_jitter: float = 0.0


@dataclass
class RandomizationConfig:
    pos_jitter: float = 0.03
    yaw_jitter: float = 30.0
    settle_steps: int = 80
    seed: int | None = None
    task_ids: tuple[str, ...] = tuple(sorted(TASKS))
    runtime_dr: RuntimeDR = field(default_factory=RuntimeDR)


class EnvRandomizer:
    """Reset object poses and sample a language-conditioned sorting task."""

    def __init__(self, bundle, config: RandomizationConfig | None = None):
        self.bundle = bundle
        self.cfg = config or RandomizationConfig()
        self.rng = np.random.default_rng(self.cfg.seed)
        self._assets = get_mesh_assets()
        self.names = list(OBJECT_LAYOUT)
        self.home = {n: np.asarray(OBJECT_LAYOUT[n]["pos"][:2], dtype=float) for n in self.names}
        self.home_yaw = {n: float(OBJECT_LAYOUT[n]["euler"][2]) for n in self.names}
        self.radius = {n: self._assets[n].radius_xy for n in self.names}
        self.rest_z = {n: self._assets[n].rest_z_offset for n in self.names}
        self.safe_jitter = self._compute_safe_jitter()
        self._base_cam_pos = np.asarray(WORLD_CAM_POS, dtype=float)
        self._base_cam_lookat = np.asarray(WORLD_CAM_LOOKAT, dtype=float)
        self._base_mass: dict[str, float] = {}
        self._capture_base_mass()

    def _capture_base_mass(self) -> None:
        for name, ent in self.bundle.objects.items():
            try:
                mass = ent.get_mass()
                if hasattr(mass, "detach"):
                    mass = mass.detach().cpu().numpy()
                self._base_mass[name] = float(np.asarray(mass).reshape(-1)[0])
            except Exception:
                self._base_mass[name] = 0.05

    def _compute_safe_jitter(self) -> dict[str, float]:
        safe: dict[str, float] = {}
        for name in self.names:
            gaps = []
            for other in self.names:
                if other == name:
                    continue
                dist = float(np.linalg.norm(self.home[name] - self.home[other]))
                gap = dist - self.radius[name] - self.radius[other] - OVERLAP_MARGIN
                gaps.append(max(0.0, 0.5 * gap))
            safe[name] = min(self.cfg.pos_jitter, min(gaps) if gaps else self.cfg.pos_jitter)
        return safe

    def reset(self, *, seed: int | None = None, task_id: str | None = None) -> TaskSpec:
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        from genesis.utils.geom import euler_to_quat

        # Teleport robot home first.
        self.bundle.franka.set_qpos(np.array(FRANKA_QPOS))

        for name in self.names:
            jitter = self.safe_jitter[name]
            dx = float(self.rng.uniform(-jitter, jitter))
            dy = float(self.rng.uniform(-jitter, jitter))
            xy = self.home[name] + np.array([dx, dy])
            xy[0] = float(np.clip(xy[0], REACH_X[0], REACH_X[1]))
            xy[1] = float(np.clip(xy[1], REACH_Y[0], REACH_Y[1]))
            yaw = self.home_yaw[name] + float(self.rng.uniform(-self.cfg.yaw_jitter, self.cfg.yaw_jitter))
            z = TABLE_TOP_Z + self.rest_z[name]
            quat = euler_to_quat(np.array([0.0, 0.0, yaw]))
            ent = self.bundle.objects[name]
            ent.set_pos(np.array([xy[0], xy[1], z]))
            ent.set_quat(quat)

        if self.cfg.runtime_dr.enabled:
            self._apply_runtime_dr()

        for _ in range(self.cfg.settle_steps):
            self.bundle.hold_home()
            self.bundle.scene.step()
            self.bundle.update_wrist_cam()

        if task_id is None:
            task_id = str(self.rng.choice(self.cfg.task_ids))
        return get_task(task_id)

    def _apply_runtime_dr(self) -> None:
        dr = self.cfg.runtime_dr
        friction_ratio = float(self.rng.uniform(*dr.friction_ratio_range))
        for name, ent in self.bundle.objects.items():
            try:
                if hasattr(ent, "set_friction"):
                    ent.set_friction(friction_ratio)
            except Exception:
                pass
            mass_ratio = float(self.rng.uniform(*dr.mass_ratio_range))
            base = self._base_mass.get(name, 0.05)
            try:
                if hasattr(ent, "set_mass_shift"):
                    ent.set_mass_shift(base * (mass_ratio - 1.0))
            except Exception:
                pass

        if self.bundle.world_cam is not None and (dr.cam_pos_jitter > 0 or dr.cam_lookat_jitter > 0):
            pos = self._base_cam_pos.copy()
            look = self._base_cam_lookat.copy()
            if dr.cam_pos_jitter > 0:
                pos += self.rng.uniform(-dr.cam_pos_jitter, dr.cam_pos_jitter, size=3)
            if dr.cam_lookat_jitter > 0:
                look += self.rng.uniform(-dr.cam_lookat_jitter, dr.cam_lookat_jitter, size=3)
            try:
                self.bundle.world_cam.set_pose(pos=pos, lookat=look)
            except Exception:
                pass
