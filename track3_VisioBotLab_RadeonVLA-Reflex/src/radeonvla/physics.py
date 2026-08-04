"""Small rigid-body helpers shared by reset and expert control paths."""

from __future__ import annotations

from typing import Any


def zero_rigid_velocity(entity: Any) -> None:
    """Clear all generalized velocities on a Genesis rigid entity."""
    zero = getattr(entity, "zero_all_dofs_velocity", None)
    if zero is not None:
        zero()


def set_rigid_position(entity: Any, pos) -> None:
    """Teleport a rigid entity without preserving stale linear/angular motion.

    Genesis ``RigidEntity.set_pos`` supports ``zero_velocity=True``.  The
    compatibility fallback keeps the helper usable with simple test doubles and
    older Genesis builds that expose only ``zero_all_dofs_velocity``.
    """
    try:
        entity.set_pos(pos, zero_velocity=True)
    except TypeError:
        entity.set_pos(pos)
        zero_rigid_velocity(entity)


def set_rigid_quaternion(entity: Any, quat) -> None:
    """Set rigid orientation and clear generalized velocity."""
    try:
        entity.set_quat(quat, zero_velocity=True)
    except TypeError:
        entity.set_quat(quat)
        zero_rigid_velocity(entity)
