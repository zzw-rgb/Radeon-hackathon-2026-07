# RadeonVLA-Reflex

> **Language:** English (official submission). Chinese version: [README.zh-CN.md](README.zh-CN.md).  
> Contest materials and PR text must be in English per the official repository rules.

RadeonVLA-Reflex is my Track 3 submission for the AMD AI DevMaster Hackathon
(team VisioBot Lab). I built a **language-guided dual-bowl fruit sorting** stack on
Genesis + Franka Panda, fine-tuning **SmolVLA** with LeRobot, all intended to run on a
single AMD Radeon GPU under ROCm.

Design focus of this codebase:

1. **Tiered task suite (L1–L4)** — named fruit×bowl, spatial grounding, ordered multi-object
   sequences, and attribute/rule-based sorting;
2. **Language-disambiguated dual bowls** — left vs right containers under free language;
3. **Interruptible command execution** — mid-episode language changes invalidate stale action chunks;
4. **Failure-aware recovery** — empty-grasp / timeout detection with one deterministic retry;
5. **Safety monitor** — joint bounds and rate limiting before actions enter Genesis;
6. **Single-GPU ROCm path** — simulation, data, training, inference, and evaluation on AMD Radeon;
7. **Partial multi-goal metrics** — success-by-tier and partial completion rates for long-horizon tasks.

> Status: pipeline code is complete. Measured AMD results, trained checkpoints, formal
> metrics, the final report PDF, and the demo video will be filled in after remote Radeon runs.

This directory is the self-contained submission unit. From the contest repository root,
open `track3_VisioBotLab_RadeonVLA-Reflex/` and follow this README to reproduce the work.

## Submission information

| Field | Value |
|---|---|
| Track | Track 3 — Physical AI Challenge |
| Team | VisioBot Lab |
| Project | RadeonVLA-Reflex |
| Team member | Zhenwei Zhou |
| Affiliation | Nanjing University of Science and Technology |

## Target application

The target application is flexible robotic sorting for food handling, laboratory
automation, and small-batch logistics. A natural-language command identifies a fruit
and a destination container. The policy observes the scene and robot state, predicts
continuous robot actions, and executes them in a closed loop with safety and recovery.

### Task tiers

| Tier | Name | What the policy must do | Examples |
|---|---|---|---|
| **L1** | Basic named | Fruit name + left/right bowl | `banana_left`, `plum_right` |
| **L2** | Spatial grounding | Resolve *leftmost / rightmost / nearest / farthest* after randomization | `leftmost_to_left`, `nearest_to_left` |
| **L3** | Multi-step sequence | Complete **ordered** multi-object placements in one episode | `seq_banana_left_lemon_right`, `seq_triple_sort` |
| **L4** | Attribute rules | Expand color/shape rules into multiple goals | `rule_yellow_left_purple_right` |

Suites (CLI `--suite`):

| Suite | Contents |
|---|---|
| `basic` | L1 only (6 tasks) |
| `spatial` | L2 |
| `multistep` | L3 |
| `rules` | L4 |
| `advanced` | L2+L3+L4 |
| **`full`** | **All tiers (default for record/eval)** |

Training and evaluation use **disjoint** natural-language phrasings per task. Spatial and
rule tasks are resolved at episode start by `radeonvla.grounding` after pose randomization.

## Planned system architecture

```text
Language command ───────────────────────┐
World RGB camera ───────────────────────┤
Wrist RGB camera ───────────────────────┤
Robot and gripper state ────────────────┤
                                        ↓
                              SmolVLA policy
                                        ↓
                                action chunk
                                        ↓
                         execution safety monitor
                         ├─ joint bounds / rate limit
                         ├─ command version changes
                         ├─ empty-grasp detection
                         └─ timeout + one recovery retry
                                        ↓
                    Genesis Franka dual-bowl simulation
                                        ↓
                                next observation
```

The learned stack is end-to-end joint-position control conditioned on language and
vision. Interrupt invalidation and recovery are deterministic safety layers around the
policy (they do not retrain the VLA).

## Repository layout

```text
track3_VisioBotLab_RadeonVLA-Reflex/
├── README.md                 # English (official)
├── README.zh-CN.md           # Chinese companion
├── pyproject.toml
├── environment.local.yml
├── requirements.local.txt
├── requirements.remote.txt
├── configs/
│   ├── base.yaml
│   ├── train.yaml
│   └── eval.yaml
├── src/radeonvla/
│   ├── scene.py              # Genesis dual-bowl scene
│   ├── expert.py             # scripted sorting expert
│   ├── record_dataset.py     # LeRobot data collection (pre-train)
│   ├── validate_dataset.py   # dataset QA before train
│   ├── train_policy.py       # SmolVLA / ACT training wrapper
│   ├── evaluate.py           # closed-loop eval + interrupt + recovery
│   ├── safety.py             # command session, safety, failures
│   ├── pipeline.py           # stage orchestrator / all-smoke
│   ├── benchmark.py          # throughput / latency
│   ├── setup_assets.py       # populate robot/YCB assets
│   ├── check_env.py
│   └── submission_audit.py
├── scripts/
│   ├── run_pipeline_smoke.sh
│   └── run_full_remote.sh
├── tests/
├── docs/
├── artifacts/
├── reports/
├── docker/Dockerfile
└── assets/README.md
```

Datasets, checkpoints, generated videos, experiment outputs, credentials, and private
configuration are excluded from Git.

## Dependency policy

PyTorch is installed separately from the project dependencies because its build must
match the execution platform:

- the checked local environment uses CPU-only PyTorch for imports and unit tests;
- the competition environment must use a PyTorch HIP build matching its ROCm version;
- a generic PyPI torch dependency is deliberately absent from pyproject.toml;
- installing the remaining dependencies must not replace the validated PyTorch build.

Pinned core versions:

| Component | Version |
|---|---|
| Python | 3.12 |
| PyTorch, local | 2.9.1+cpu |
| torchvision, local | 0.24.1+cpu |
| torchaudio, local | 2.9.1+cpu |
| Genesis | 1.1.2 |
| LeRobot | 0.6.0 |

The Track 3 starter currently documents a dedicated ROCm 7.2.1 wheel set. Use that set
only when the remote instance reports ROCm 7.2.1 and Python 3.12. Otherwise select the
matching official ROCm wheels before installing requirements.remote.txt.

## Local development setup

The validated local machine is Ubuntu 22.04.5 on a Lenovo Legion R7000 2021 with a
Ryzen 5 5600H, 16 GB RAM, and an NVIDIA RTX 3050. It is a development client, not the
final AMD execution machine.

### Recreate the Conda environment

```bash
conda env create -f environment.local.yml
conda activate radeonvla-dev

python -m pip install \
  --index-url https://download.pytorch.org/whl/cpu \
  torch==2.9.1+cpu \
  torchvision==0.24.1+cpu \
  torchaudio==2.9.1+cpu

python -m pip install -r requirements.local.txt
python -m pip install -e .
python -m pip check
```

### Validate the local environment

```bash
conda activate radeonvla-dev
python -m radeonvla.check_env --json docs/environment.local.json
python -m radeonvla.setup_assets
pytest
ruff check src tests
python -m radeonvla.submission_audit
```

Local results are not accepted as Radeon or ROCm evidence.

## Remote AMD Radeon setup

Use a persistent PVC-backed Radeon Cloud instance and expose exactly one GPU.
See `docs/REMOTE_ROCM_SETUP.md` for ROCm wheel details.

### 1. Audit the untouched instance

```bash
uname -a
cat /etc/os-release
python3 --version
rocminfo | head -n 100
amd-smi
python3 - <<'PY'
import torch
print("torch:", torch.__version__)
print("hip:", torch.version.hip)
print("available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
PY
```

### 2. Clone onto the persistent volume

```bash
cd <PVC_ROOT>
mkdir -p visiobot
cd visiobot
git clone https://github.com/<GITHUB_ID>/Radeon-hackathon-2026-07.git
cd Radeon-hackathon-2026-07
git checkout <SUBMITTED_COMMIT_OR_BRANCH>
cd track3_VisioBotLab_RadeonVLA-Reflex
```

### 3. Create or reuse the Python 3.12 environment

If the image already has a validated PyTorch HIP build in Python 3.12:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

### 4. Install the remaining dependencies

```bash
python -m pip install -r requirements.remote.txt
python -m pip install -e .
python -m pip check
python - <<'PY'
import torch
assert torch.version.hip is not None
assert torch.cuda.is_available()
print(torch.__version__, torch.version.hip, torch.cuda.get_device_name(0))
PY
```

### 5. Strict AMD validation

```bash
export HIP_VISIBLE_DEVICES=0
bash scripts/check_remote_amd.sh
```

## End-to-end pipeline (implemented)

All stages below are implemented as `python -m radeonvla.<module>` entry points.

| Stage | Module | Purpose |
|---|---|---|
| Assets | `setup_assets` | Copy Franka + YCB meshes into `assets/` |
| Env check | `check_env` | Torch / HIP / Genesis report |
| Scene | `scene` | Dual-bowl Genesis smoke + optional frames |
| Expert | `expert` | Scripted language-conditioned pick-and-place |
| **Record** | **`record_dataset`** | **Collect LeRobot demos (required before train)** |
| Validate | `validate_dataset` | Schema / NaN / image checks on the dataset |
| Train | `train_policy` | SmolVLA / ACT via `lerobot-train` |
| Evaluate | `evaluate` | Closed-loop policy + interrupt + recovery |
| Benchmark | `benchmark` | Sim SPS / optional inference latency |
| Pipeline | `pipeline` | Orchestrate stages (`all-smoke`, etc.) |

### One-click scripts (recommended)

| Script / Make target | What it does |
|---|---|
| `bash scripts/run_all_local.sh` / `make all-local` | Local one-click: assets → scene → expert → **record** → validate |
| `bash scripts/run_record.sh` / `make record-local` | Record demos only (`EPISODES`, `SUITE`, `BACKEND` overridable) |
| `bash scripts/run_expert_demo.sh` / `make expert-demo` | Scripted demos (basic / hard mix) |
| `bash scripts/run_pipeline_smoke.sh` / `make smoke` | 1-episode smoke + train dry-run |
| `bash scripts/run_full_remote.sh` / `make remote-full` | Full AMD: check → record → train → eval → benchmark |
| `bash scripts/check_local.sh` / `make check` | Env + audit + pytest + ruff |
| `bash scripts/check_remote_amd.sh` / `make remote-check` | Strict ROCm gate |

```bash
# Local: collect 10 basic episodes
EPISODES=10 SUITE=basic bash scripts/run_record.sh

# Local: full one-click pipeline
EPISODES=5 bash scripts/run_all_local.sh

# Fast smoke
make smoke

# On AMD Radeon
EPISODES=100 SUITE=full bash scripts/run_full_remote.sh
```

Details and env vars: [`scripts/README.md`](scripts/README.md). Optional `.env` from `.env.example`.

### One-shot local smoke (module form)

```bash
bash scripts/run_pipeline_smoke.sh
# equivalent:
python -m radeonvla.pipeline all-smoke --backend cpu --episodes 1 --task banana_left
```

This runs assets → env → scene → expert(1) → **record(1)** → validate → train dry-run.

### Step-by-step commands

```bash
# Environment & assets
python -m radeonvla.check_env
python -m radeonvla.check_env --require-amd --init-genesis
python -m radeonvla.setup_assets
python -m radeonvla.submission_audit

# M1 — scene smoke test
python -m radeonvla.scene --backend cpu --steps 100 --save-frames
python -m radeonvla.scene --backend amdgpu --steps 100 --save-frames

# M2 — scripted expert (basic + hard multi-step)
python -m radeonvla.expert --task banana_left --episodes 5 --backend cpu
python -m radeonvla.expert --task seq_triple_sort --episodes 3 --backend cpu
python -m radeonvla.expert --suite advanced --episodes 8 --backend amdgpu

# M3 — data collection (default suite=full includes L1–L4)
python -m radeonvla.record_dataset \
  --episodes 100 \
  --suite full \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --backend amdgpu \
  --overwrite

# Ablation: basic-only data
python -m radeonvla.record_dataset --episodes 50 --suite basic --overwrite \
  --repo-id visiobot/radeonvla_basic --dataset-root datasets/radeonvla_basic

# Optional domain randomization while recording
python -m radeonvla.record_dataset --episodes 100 --dr-appearance --dr-object-color \
  --dr-runtime --backend amdgpu --overwrite

# Validate dataset before train
python -m radeonvla.validate_dataset \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex

# M4/M5 — train SmolVLA (needs a non-empty recorded dataset)
python -m radeonvla.train_policy smolvla \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --steps 10000 --device cuda

# Closed-loop evaluation (interrupt + recovery)
python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex/checkpoints/last/pretrained_model \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --episodes-per-task 10 --save-video --backend amdgpu

# Interruptibility demo (injects a mid-episode command change on ep0)
python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex/checkpoints/last/pretrained_model \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --interrupt-demo --save-video --backend amdgpu

# Throughput / latency
python -m radeonvla.benchmark --backend amdgpu --steps 500
```

### Full remote script (AMD)

```bash
export HIP_VISIBLE_DEVICES=0
bash scripts/run_full_remote.sh
# or customize:
EPISODES=100 TRAIN_STEPS=10000 bash scripts/run_full_remote.sh
```

Optional Docker (preferable for Track 3):

```bash
docker build -f docker/Dockerfile -t radeonvla-reflex:rocm7.2.1 .
docker run --rm -it --device=/dev/kfd --device=/dev/dri \
  --group-add video --group-add render \
  -v "$PWD":/workspace/radeonvla-reflex \
  radeonvla-reflex:rocm7.2.1
```

## Dataset specification

Each frame contains:

```text
observation.images.world   # HWC uint8 RGB
observation.images.wrist   # HWC uint8 RGB
observation.state          # 9-D qpos (7 arm + 2 fingers)
action                     # 9-D absolute joint-position target
task                       # natural-language instruction
```

| Item | Value |
|---|---|
| Action type | absolute joint position |
| Dimension | 9 |
| Joint order | panda_joint1..7, panda_finger_joint1..2 |
| Gripper range | [0.0, 0.04] m |
| Control / dataset FPS | 20 Hz (sim 100 Hz, decimated) |
| Image size | 320×240 |

Seed splits:

| Split | Seeds |
|---|---|
| Training | 0–9999 |
| Validation | 10000–10999 |
| Formal evaluation | 20000–29999 |
| Interrupt / recovery | 30000–30999 |

## Evaluation protocol

The minimum formal evaluation is 20 held-out episodes across at least two tasks. The
target protocol is 10 held-out episodes for each of the six tasks (evaluation language).

Reported metrics:

- task success rate;
- object accuracy;
- target accuracy;
- first-attempt success;
- final success after the allowed recovery;
- recovery success;
- mean and P95 completion time;
- P50 and P95 inference latency;
- simulation steps per second;
- training samples per second;
- training and inference peak VRAM.

Every episode, including failures, remains in the raw JSON results under
`outputs/eval_results/`. Schema: `artifacts/evaluation.schema.json`.

## Reproduction sequence

1. clone the repository at the submitted commit;
2. configure a matching ROCm/PyTorch environment;
3. install project dependencies (`requirements.remote.txt` + `pip install -e .`);
4. run `python -m radeonvla.setup_assets` (or provide assets as documented);
5. run strict AMD environment validation;
6. smoke-test the Genesis scene;
7. record demos / download the public dataset revision;
8. train or download the public SmolVLA checkpoint;
9. run held-out evaluation and write JSON + videos;
10. compare generated metadata with the technical report.

No private account, unpublished file, or source edit should be required for the final
release revision.

## Deliverables

| Deliverable | Status | Link |
|---|---|---|
| Source code | Pipeline implemented | This self-contained directory |
| Reproducibility README | This file | README.md |
| Technical report (MD) | Draft structure | reports/RadeonVLA-Reflex-Technical-Report.md |
| Technical report PDF | TODO | TBD |
| Demo video | TODO | TBD |
| Model checkpoint | TODO | TBD |
| Dataset or dataset documentation | Template | docs/DATASET_CARD.md |
| Raw evaluation results | TODO | TBD |
| SHA256 checksums | TODO | TBD |
| Docker image definition | Available | docker/Dockerfile |

Submission-authoring files:

- `docs/DATASET_CARD.md`
- `docs/MODEL_CARD.md`
- `reports/RadeonVLA-Reflex-Technical-Report.md`

```bash
python -m radeonvla.submission_audit
python -m radeonvla.submission_audit --final   # fails until PDF + checksums exist
```

## References and attribution

- AMD Track 3 contest repository
- AMD Radeon Cloud User Guide
- Track 3 Franka fruit-pick demo (workflow reference for Genesis + LeRobot on ROCm)
- Genesis World
- Hugging Face LeRobot / SmolVLA
- YCB Object and Model Set

I studied upstream repositories outside this submission directory. This tree is original
project code for RadeonVLA-Reflex; see THIRD_PARTY_NOTICES.md for dependency notices.

## Team

- Zhenwei Zhou — system design, implementation, training, evaluation, and submission
- VisioBot Lab
- Nanjing University of Science and Technology

## Submission

Official Pull Request title:

```text
Track 3, VisioBot Lab, RadeonVLA-Reflex
```

All submission materials, project descriptions, and Pull Request text will be in English.
