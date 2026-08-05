# RadeonVLA-Reflex

> **Language:** English project guide. Chinese version: [README.zh-CN.md](README.zh-CN.md).
> Release materials and Pull Request text use English under the repository rules.

RadeonVLA-Reflex is an **interruptible and recoverable VLA execution runtime** for
dynamic robotic sorting on one AMD Radeon GPU. The Track 3 benchmark uses a Franka
Panda, Genesis, LeRobot, and SmolVLA to sort five fruits into four language-addressable
bowls. Fruit sorting is the testbed; the core contribution is keeping action-chunking
policies responsive when an operator changes a command or a grasp fails.

Design focus of this codebase:

1. **Tiered task suite (L1–L4)** — named fruit×bowl, spatial grounding, ordered multi-object
   sequences, and attribute/rule-based sorting;
2. **Language-disambiguated dual bowls** — left vs right containers under free language;
3. **Interruptible command execution** — mid-episode language changes invalidate stale action chunks;
4. **Failure-aware recovery** — empty-grasp / timeout detection, deterministic retreat/retry, and an explicit strict-physics precision fallback;
5. **Safety monitor** — joint bounds and rate limiting before actions enter Genesis;
6. **Single-GPU ROCm path** — simulation, data, training, inference, and evaluation on AMD Radeon;
7. **Partial multi-goal metrics** — success-by-tier and partial completion rates for long-horizon tasks.
8. **Repeatable stress tests** — deterministic target/container shifts with normal-vs-Reflex ablations;
9. **Structured evidence** — per-episode JSON, flattened CSV, Markdown summaries, videos with live
   runtime state, and deterministic checkpoint hashes;
10. **Crash-safe collection** — incomplete runs remain in a staging directory and never replace the
    last validated dataset.

> Release status (2026-08-05): the strict 20×100 Physical-2K dataset and cumulative ~200K-step
> SmolVLA inference tree are complete. On the fixed 20-task × 5-seed benchmark, learned
> first-attempt success is **36/100** and the explicit strict-physics Precision-Reflex system
> finishes **91/100** (Wilson 95% CI **83.8–95.2%**). All 100 episodes, including nine failures,
> remain in the immutable result bundle.

| Public artifact | Immutable revision |
|---|---|
| [Physical-2K dataset](https://huggingface.co/datasets/a3124371940/radeonvla_reflex_physical_2k) — 2,000 episodes / 468,889 frames | `2779b7c5566df9072bb9a7c43335d6203ea97887` |
| [Cumulative 200K SmolVLA checkpoint](https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_2k_200k) | `1ea32da3d59ce0905d0f1331bc3c6643e42beb7e` |
| [Cumulative 50K SmolVLA checkpoint](https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_1k_50k) | `59f6f0ad720054505667a652fe07e03d65e82915` |
| [Physical-1K dataset](https://huggingface.co/datasets/a3124371940/radeonvla_reflex_physical_1k) — 1,000 episodes / 232,658 frames | `b0f72c60e9100739fd82bd498c8f3d9bed7b75af` |
| [SmolVLA-1K checkpoint](https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_1k) — 20,000 steps | `abcca9f2b313e378b554449016b520b8117016fe` |

Live showcase: **https://zzw-rgb.github.io/Radeon-hackathon-2026-07/**

This directory is the self-contained project unit. From the repository root, open
`track3_VisioBotLab_RadeonVLA-Reflex/` and follow this README to reproduce the system.

## Project information

| Field | Value |
|---|---|
| Track | Track 3 — Physical AI Challenge |
| Team | VisioBot Lab |
| Project | RadeonVLA-Reflex |
| Captain | Zhenwei Zhou |
| Members | Ange Liu, Haoran Wang |
| Affiliation | Nanjing University of Science and Technology |

## Target application

The target application is a language-reconfigurable sorting cell for food handling,
laboratory automation, and small-batch logistics. An operator can change a destination
while the robot is moving without waiting for a pre-generated action chunk to finish.
The runtime invalidates stale actions, moves to a safe open-gripper hold, and can retry
detected failures with a bounded controller; precision mode still forbids object teleport and
grasp glue. This reduces the need for task-specific PLC reprogramming while
keeping operator intervention explicit and measurable.

### Task tiers

| Tier | Name | What the policy must do | Examples |
|---|---|---|---|
| **L1** | Basic named | Fruit × bowl (5 fruits × 4 bowls) | `banana_white_left`, `apple_blue_left`, `orange_blue_right` |
| **L2** | Spatial grounding | Resolve *leftmost / rightmost / nearest / farthest* after randomization | `leftmost_to_white_left`, `leftmost_to_blue_left` |
| **L3** | Multi-step sequence | Complete **ordered** multi-object placements in one episode | `seq_banana_white_left_lemon_white_right`, `seq_apple_blue_left_orange_blue_right` |
| **L4** | Attribute rules | Expand color/shape rules into multiple goals | `rule_yellow_white_left_purple_white_right`, `rule_red_blue_left_orange_blue_right` |

Scene objects: **banana, lemon, plum, apple, orange** and **four upright bowls** —
**left: white + blue**, **right: white + blue** (all placeable; bowls are fixed so they do not tip).

Suites (CLI `--suite`):

| Suite | Contents |
|---|---|
| `basic` | L1 only (20 tasks) |
| `spatial` | L2 |
| `multistep` | L3 |
| `rules` | L4 |
| `advanced` | L2+L3+L4 |
| `full` | All tiers (explicit opt-in advanced benchmark) |

Physical-2K stores two deterministic collected phrasings per task. The primary controller
benchmark reuses those exact strings with disjoint seeds; `--instruction-source heldout`
is a separate paraphrase-generalization test. Spatial and rule tasks are resolved at
episode start by `radeonvla.grounding` after pose randomization.

## System architecture

![RadeonVLA-Reflex system architecture: dual RGB cameras and robot state condition a SmolVLA policy; action chunks pass through an execution safety monitor with command invalidation, failure detection, bounded strict-physics recovery, and latency telemetry before Genesis Franka dual-bowl simulation](docs/figures/architecture-en.jpg)

The closed loop is:

1. **Perception + state** — world RGB, wrist RGB, and robot/gripper state (joint positions \(q\), velocities \(\dot q\), gripper opening \(g\), end-effector pose \(T\)).
2. **SmolVLA policy** — vision-language-action model produces action chunks (\(\Delta q\), \(\Delta g\), \(\Delta T\)).
3. **Execution safety monitor (Reflex)** — joint/velocity limits, command-version invalidation, empty-grasp detection and deterministic retreat; explicit `--precision-recovery` invokes a strict-physics geometric fallback after learned-control failure and reports its contribution separately.
4. **Genesis Franka dual-bowl simulation** — executes only the safe command; next observation feeds back into the loop.

The learned stack is end-to-end joint-position control conditioned on language and
vision. Interrupt invalidation and recovery are **deterministic safety layers around the
policy** (they do not retrain the VLA). Evaluation can inject a repeatable target or bowl
shift and renders `RUNNING / INTERRUPTED / RECOVERING / PRECISION RECOVERY / SUCCESS` directly on demo video.

Chinese diagram: [`docs/figures/architecture-zh.jpg`](docs/figures/architecture-zh.jpg).

## Repository layout

```text
track3_VisioBotLab_RadeonVLA-Reflex/
├── README.md                 # English project guide
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
│   ├── stress.py             # deterministic target/container perturbations
│   ├── artifact_io.py        # hashes + JSON/CSV/Markdown evidence
│   ├── vendor_vlm_assets.py  # offline SmolVLM config/tokenizer bundle
│   ├── safety.py             # command session, safety, failures
│   ├── pipeline.py           # stage orchestrator / all-smoke
│   ├── benchmark.py          # throughput / latency
│   ├── setup_assets.py       # populate robot/YCB assets
│   ├── check_env.py
│   └── submission_audit.py
├── scripts/
│   ├── run_pipeline_smoke.sh
│   ├── run_reflex_demo.sh
│   └── run_full_remote.sh
├── tests/
├── docs/
├── artifacts/
├── reports/
├── docker/
│   ├── Dockerfile
│   ├── compose.yaml
│   └── entrypoint.sh
├── .dockerignore
└── assets/README.md
```

Datasets, checkpoints, generated videos, experiment outputs, credentials, and private
configuration are excluded from Git.

## Dependency policy

PyTorch is installed separately from the project dependencies because its build must
match the execution platform:

- the checked local environment uses CPU-only PyTorch for imports and unit tests;
- the remote Radeon environment must use a PyTorch HIP build matching its ROCm version;
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

## Assets (required for reproduction)

Mesh assets are **committed in this repository** under `assets/` (~42 MB) so a normal
clone is enough to run the scene without private file shares:

| Path | Content |
|---|---|
| `assets/ycb/011_banana`, `013_apple`, `014_lemon`, `017_orange`, `018_plum`, `024_bowl` | YCB meshes |
| `assets/robots/franka/` | Franka Emika Panda MJCF |
| `assets/SHA256SUMS` | Integrity checksums |

```bash
python -m radeonvla.setup_assets          # no-op when files already present
python -m radeonvla.setup_assets --verify # check SHA256
python -m radeonvla.setup_assets --download  # optional network fallback if files were deleted
```

Upstream sources and redistribution notes: [`assets/README.md`](assets/README.md),
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

- YCB Object and Model Set: https://www.ycbbenchmarks.com/object-models/
- YCB data portal: http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/
- Genesis (Franka model also recoverable from the installed package): https://github.com/Genesis-Embodied-AI/Genesis

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

Local runs validate portability and code quality but are excluded from Radeon performance metrics.

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
cd /workspace
mkdir -p visiobot
cd visiobot
git clone https://github.com/zzw-rgb/Radeon-hackathon-2026-07.git
cd Radeon-hackathon-2026-07
git checkout submission/track3-visiobotlab-radeonvla-reflex
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

### Standard workflow scripts

| Script / Make target | What it does |
|---|---|
| `bash scripts/run_all_local.sh` / `make all-local` | Local one-click: assets → scene → expert → **record** → validate |
| `bash scripts/run_record.sh` / `make record-local` | Record demos only (`EPISODES`, `SUITE`, `BACKEND` overridable) |
| `bash scripts/run_expert_demo.sh` / `make expert-demo` | Scripted demos (basic / hard mix) |
| `bash scripts/run_pipeline_smoke.sh` / `make smoke` | 1-episode smoke + train dry-run |
| `bash scripts/run_full_remote.sh` / `make remote-full` | Full AMD: check → record → train → eval → benchmark |
| `bash scripts/run_reflex_demo.sh` | Normal + command-interrupt + target-shift policy recordings |
| `bash scripts/check_local.sh` / `make check` | Env + audit + pytest + ruff |
| `bash scripts/check_remote_amd.sh` / `make remote-check` | Strict ROCm gate |

```bash
# Local: collect 10 basic episodes
EPISODES=10 SUITE=basic bash scripts/run_record.sh

# Local: full one-click pipeline
EPISODES=5 bash scripts/run_all_local.sh

# Fast smoke
make smoke

# On AMD Radeon: 10 successful demonstrations for each of 20 L1 variations
EPISODES=200 SUITE=basic bash scripts/run_full_remote.sh
```

Details and env vars: [`scripts/README.md`](scripts/README.md). Optional `.env` from `.env.example`.

### One-shot local smoke (module form)

```bash
bash scripts/run_pipeline_smoke.sh
# equivalent:
python -m radeonvla.pipeline all-smoke --backend cpu --episodes 1 --task banana_white_left
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
python -m radeonvla.expert --task banana_white_left --episodes 5 --backend cpu
python -m radeonvla.expert --task seq_triple_sort --episodes 3 --backend cpu
python -m radeonvla.expert --suite advanced --episodes 8 --backend amdgpu

# M3 — primary L1 data collection (20 tasks × 10 successful demonstrations)
python -m radeonvla.record_dataset \
  --episodes 200 \
  --suite basic \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --backend amdgpu \
  --require-coverage

# Explicitly replace an existing published dataset only after the new run validates
python -m radeonvla.record_dataset --episodes 200 --suite basic --require-coverage \
  --overwrite --discard-incomplete --repo-id visiobot/radeonvla_basic \
  --dataset-root datasets/radeonvla_basic

# Optional domain randomization while recording
python -m radeonvla.record_dataset --episodes 400 --suite basic --require-coverage \
  --dr-appearance --dr-object-color --dr-runtime --backend amdgpu

# Formal strict-physics dataset: exactly 20 tasks × 50 successful episodes.
# Kinematic grasp assist, object teleports, and placement nudges are disabled;
# every committed episode receives an atomic provenance certificate.
SOURCE_COMMIT="$(git rev-parse HEAD)" python -m radeonvla.record_dataset \
  --episodes-per-task 50 --suite basic --require-coverage \
  --repo-id YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --dr-appearance --dr-object-color --dr-runtime --dr-rebuild-every 20 \
  --max-attempts 10000 --backend amdgpu

# Continue the same staging dataset after an interruption. All collection
# settings and the source revision must match the atomic progress record.
SOURCE_COMMIT="$(git rev-parse HEAD)" python -m radeonvla.record_dataset \
  --episodes-per-task 50 --suite basic --require-coverage \
  --repo-id YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --dr-appearance --dr-object-color --dr-runtime --dr-rebuild-every 20 \
  --max-attempts 10000 --backend amdgpu --resume-incomplete

# Validate dataset before train
python -m radeonvla.validate_dataset \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex

# Formal publication gate
python -m radeonvla.validate_dataset \
  --repo-id YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --expected-episodes 1000 --episodes-per-task 50 --require-strict-physics

# Release authentication uses an interactive login after measured card metadata
# is available. The write token stays out of commands, repository files, and shell history.
hf auth login

# Publish private first. The command validates 20×50, uploads the full dataset
# and self-contained checkpoint, then reloads both from immutable Hub revisions.
python -m radeonvla.publish_hf \
  --dataset-repo YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --dataset-validation artifacts/dataset_validation_physical_1k.json \
  --model-repo YOUR_HF_NAMESPACE/radeonvla-reflex-smolvla-1k \
  --policy-path outputs/train/smolvla_physical_1k/checkpoints/020000/pretrained_model \
  --private

# Make the already verified release public only with an explicit confirmation.
python -m radeonvla.publish_hf \
  --dataset-repo YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --dataset-validation artifacts/dataset_validation_physical_1k.json \
  --model-repo YOUR_HF_NAMESPACE/radeonvla-reflex-smolvla-1k \
  --policy-path outputs/train/smolvla_physical_1k/checkpoints/020000/pretrained_model \
  --public --confirm-public-release

# M4/M5 — train SmolVLA (needs a non-empty recorded dataset)
python -m radeonvla.train_policy smolvla \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --steps 10000 --device cuda

# Formal 100-rollout Precision-Reflex benchmark (20 tasks × 5 seeds)
python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex_physical_2k_continue_100k_to200k/checkpoints/100000/pretrained_model \
  --repo-id a3124371940/radeonvla_reflex_physical_2k \
  --dataset-root datasets/radeonvla_reflex_physical_2k \
  --suite basic --episodes 100 --seed-start 52000 \
  --instruction-source collected --max-retries 0 --precision-recovery \
  --backend amdgpu --output artifacts/evaluation.precision_reflex_basic100.json

# Interruptibility demo (injects a mid-episode command change on ep0)
python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex/checkpoints/last/pretrained_model \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --tasks banana_white_left --interrupt-demo --save-video --backend amdgpu \
  --output artifacts/interrupt_evaluation.json

# Repeatable robustness stress: move the active target during execution
python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex/checkpoints/last/pretrained_model \
  --repo-id visiobot/radeonvla_reflex --dataset-root datasets/radeonvla_reflex \
  --tasks banana_white_left lemon_blue_right plum_white_right \
  --episodes-per-task 2 --perturbation target_shift --perturb-at-step 30 \
  --save-video --backend amdgpu --output artifacts/perturbation_evaluation.json

# Throughput / latency
python -m radeonvla.benchmark --backend amdgpu --steps 500
```

### Full remote script (AMD)

```bash
export HIP_VISIBLE_DEVICES=0
bash scripts/run_full_remote.sh
# or customize:
EPISODES=200 SUITE=basic TRAIN_STEPS=10000 bash scripts/run_full_remote.sh
```

### Self-contained Docker runtime

```bash
docker build --pull -f docker/Dockerfile -t radeonvla-reflex:rocm7.2.1 .
docker run --rm -it --device=/dev/kfd --device=/dev/dri \
  --group-add video --group-add render \
  --ipc=host --shm-size=8g --security-opt seccomp=unconfined \
  -v "$PWD/datasets":/workspace/radeonvla-reflex/datasets \
  -v "$PWD/checkpoints":/workspace/radeonvla-reflex/checkpoints \
  -v "$PWD/outputs":/workspace/radeonvla-reflex/outputs \
  -v "$PWD/artifacts":/workspace/radeonvla-reflex/artifacts \
  radeonvla-reflex:rocm7.2.1 check-amd

# Equivalent Compose entry point
docker compose -f docker/compose.yaml run --rm radeonvla check-amd
```

The source, configs, scripts, assets, report sources, and tests are inside the image;
only mutable datasets, checkpoints, outputs, and evidence are mounted. Container commands
are `help`, `check-amd`, `smoke`, `remote-full`, `reflex-demo`, and `shell`.

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
| Strict smoke | 12000–12999 |
| Training sources | 21000–26999 and 71000–76039 |
| Validation | 40000–40999 |
| Formal 100-rollout evaluation | 52000–52099 |
| Interrupt / recovery | 60000–60999 |

## Evaluation protocol

The primary release protocol is five disjoint-seed episodes for each of the 20 L1 tasks
(100 total) using the exact collected language. The held-out paraphrase suite is separate.
Additional interrupt and target-shift suites use representative tasks and disjoint seeds.
L2–L4 results are reported only when trained and measured.

Reported metrics:

- task success rate;
- object accuracy;
- target accuracy;
- first-attempt success;
- final success after the allowed recovery;
- recovery success;
- safe interrupt rate and command-to-invalidation steps;
- success by task and injected perturbation scenario;
- mean and P95 completion time;
- P50 and P95 inference latency;
- simulation steps per second;
- training samples per second;
- training and inference peak VRAM.

Every episode, including failures, remains in JSON. Canonical evidence is written to
`artifacts/evaluation.json`, `evaluation.csv`, and `summary.md`; schema:
`artifacts/evaluation.schema.json`. Videos include the current command, Reflex state,
command version, retry count, scenario, and measured inference latency.

## Reproduction sequence

1. clone the repository at the release commit;
2. configure a matching ROCm/PyTorch environment;
3. install project dependencies (`requirements.remote.txt` + `pip install -e .`);
4. run `python -m radeonvla.setup_assets` (or provide assets as documented);
5. run strict AMD environment validation;
6. smoke-test the Genesis scene;
7. record demos / download the public dataset revision;
8. train or download the public SmolVLA checkpoint;
9. run held-out evaluation and write JSON + videos;
10. compare generated metadata with the technical report.

The final release revision requires no private account, unpublished file, or source edit.

## Deliverables

| Deliverable | Status | Link |
|---|---|---|
| Source code | Public release branch | [GitHub source](https://github.com/zzw-rgb/Radeon-hackathon-2026-07/tree/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex) |
| Reproducibility README | This file | README.md |
| Technical report (MD) | Maintained source | reports/RadeonVLA-Reflex-Technical-Report.md |
| Technical report PDF | A4, 5 pages, final audit input | [Technical report PDF](reports/RadeonVLA-Reflex-Technical-Report.pdf) |
| Public showcase | GitHub Pages deployment verified | [RadeonVLA-Reflex website](https://zzw-rgb.github.io/Radeon-hackathon-2026-07/) |
| 3+ minute narrated demo | 200.0 s, 1080p30 H.264/AAC, natural English narration and burned English captions | [Play public video](https://zzw-rgb.github.io/Radeon-hackathon-2026-07/videos/radeonvla-reflex-3min.mp4) |
| Paired recovery evidence | 15.0 s, same task and seed | `website/public/videos/normal-vs-reflex-15s.mp4` |
| Mid-command change evidence | Safe interrupt 1/1; 0 unprotected stale steps | `artifacts/interrupt_evaluation.json` |
| Model checkpoint | Public 200K checkpoint, revision `1ea32da3…beb7e` | [Hugging Face model](https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_2k_200k) |
| Dataset | Physical-2K, revision `2779b7c5…97887` | [Hugging Face dataset](https://huggingface.co/datasets/a3124371940/radeonvla_reflex_physical_2k) |
| Raw evaluation results | 100/100 episodes retained | `artifacts/evaluation.json`, `.csv`, `summary.md` |
| SHA256 checksums | Final release bundle | `artifacts/SHA256SUMS` |
| Docker image definition | Self-contained runtime definition | docker/Dockerfile |

Release documentation:

- `docs/DATASET_CARD.md`
- `docs/MODEL_CARD.md`
- `reports/RadeonVLA-Reflex-Technical-Report.md`

```bash
python -m radeonvla.submission_audit
python -m radeonvla.submission_audit --final
```

## References and attribution

- AMD Track 3 contest repository
- AMD Radeon Cloud User Guide
- Track 3 Franka fruit-pick demo (workflow reference for Genesis + LeRobot on ROCm)
- Genesis World
- Hugging Face LeRobot / SmolVLA
- YCB Object and Model Set

Upstream repositories are maintained outside this project directory. This tree contains
the RadeonVLA-Reflex project code; dependency notices are listed in THIRD_PARTY_NOTICES.md.

## Team

**VisioBot Lab** · Nanjing University of Science and Technology

| Member | Role | Effort | Focus |
|---|---|---:|---|
| **Zhenwei Zhou** | Team captain / lead engineer | ~70% | System architecture, Genesis scene & expert, strict-physics collection, SmolVLA train/eval, website, and release engineering |
| Ange Liu | Member | ~15% | Bilingual documentation polish, task-suite wording review, showcase copy support |
| Haoran Wang | Member | ~15% | Dataset spot-checks, experiment logging, technical-report / evidence packaging support |

## Submission

Official Pull Request title:

```text
Track 3, VisioBot Lab, RadeonVLA-Reflex
```

Submission materials, project descriptions, and Pull Request text use English.
The concise evaluator-facing submission brief is [`docs/SUBMISSION.md`](docs/SUBMISSION.md).
