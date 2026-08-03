from radeonvla.config import load_config
from radeonvla.paths import PROJECT_ROOT
from radeonvla.protocol import ACTION_DIM, JOINT_NAMES, SMOLVLA_RENAME_MAP, dataset_features
from radeonvla.train_policy import PRESETS, build_command


def test_dataset_features_shapes() -> None:
    feats = dataset_features(240, 320)
    assert feats["observation.state"]["shape"] == (ACTION_DIM,)
    assert feats["action"]["names"] == list(JOINT_NAMES)
    assert feats["observation.images.world"]["shape"] == (240, 320, 3)


def test_load_train_config_inherits_base() -> None:
    cfg = load_config(PROJECT_ROOT / "configs" / "train.yaml")
    assert cfg["project"] == "RadeonVLA-Reflex"
    assert cfg["policy"]["type"] == "smolvla"
    assert cfg["runtime"]["control_hz"] == 20
    assert cfg["action"]["dimension"] == 9


def test_smolvla_train_command_includes_rename_map() -> None:
    class Args:
        policy = "smolvla"
        policy_path = None
        policy_type = None
        dataset_root = "datasets/demo"
        repo_id = "visiobot/demo"
        batch_size = None
        name = None
        output_dir = None
        steps = 100
        save_freq = 50
        log_freq = 10
        num_workers = 0
        seed = 0
        device = "cpu"
        push_to_hub = False
        wandb = False
        video_backend = "pyav"
        rename_map = None

    cmd = build_command(Args(), [])
    joined = " ".join(cmd)
    assert "lerobot.scripts.lerobot_train" in joined
    assert "rename_map" in joined
    assert PRESETS["smolvla"]["rename_map"] == SMOLVLA_RENAME_MAP
