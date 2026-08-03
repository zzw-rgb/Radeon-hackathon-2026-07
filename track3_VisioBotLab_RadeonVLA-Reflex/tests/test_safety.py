from radeonvla.protocol import GRIPPER_OPEN, clamp_action
from radeonvla.safety import CommandSession, FailureReason, RecoveryPolicy, SafetyMonitor
from radeonvla.tasks import get_task


def test_clamp_action_bounds() -> None:
    raw = [10.0, -10.0, 0.0, -4.0, 0.0, 5.0, 0.0, 1.0, -1.0]
    out = clamp_action(raw)
    assert out[0] <= 2.80
    assert out[1] >= -1.70
    assert 0.0 <= out[7] <= 0.04
    assert 0.0 <= out[8] <= 0.04


def test_command_session_versions_on_change() -> None:
    session = CommandSession(instruction="a", task_id="banana_left")
    assert session.version == 0
    v1 = session.set_command(instruction="b", task_id="banana_right", step=10)
    assert v1 == 1
    assert session.is_current(1)
    assert not session.is_current(0)
    assert session.events[-1]["type"] == "command_change"


def test_safety_monitor_invalidates_chunk_on_command_change() -> None:
    monitor = SafetyMonitor(max_joint_delta=0.5)
    action = [0.0, -0.3, 0.0, -2.0, 0.0, 1.7, 0.79, 0.0, 0.0]
    d0 = monitor.process(action, command_version=0)
    assert d0.accepted
    d1 = monitor.process(action, command_version=1)
    assert d1.invalidate_chunk
    assert d1.reason == "command_invalidated"
    assert d1.action[7] == GRIPPER_OPEN


def test_recovery_policy_limits_retries() -> None:
    policy = RecoveryPolicy(max_retries=1)
    assert policy.should_retry(0, FailureReason.EMPTY_GRASP)
    assert not policy.should_retry(1, FailureReason.EMPTY_GRASP)
    action = policy.recovery_action()
    assert len(action) == 9
    assert action[7] == GRIPPER_OPEN


def test_task_registry_language_disjoint() -> None:
    task = get_task("banana_left")
    assert set(task.training_instructions).isdisjoint(task.evaluation_instructions)
