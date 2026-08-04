# RadeonVLA-Reflex

> **语言：** 中文说明。英文正式版见 [README.md](README.md)。  
> 比赛提交材料与 Pull Request 正文请使用英文（官方仓库要求）。

RadeonVLA-Reflex 是运行在单张 AMD Radeon GPU 上的**可中断、可恢复 VLA 执行层**。
Track 3 基准使用 Genesis、Franka Panda、LeRobot 和 SmolVLA，把 5 种水果分到 4 个
可由语言指定的盘位。水果分拣是验证场景，核心贡献是让 action-chunk 策略在操作员改指令
或抓取失败时仍能及时、安全、可量化地响应。

主要设计内容：

1. **分级任务套件（L1–L4）** — 命名目标、空间指代、有序多物体序列、属性/规则分拣；
2. **语言可区分的双碗** — 左/右容器需由自然语言消歧；
3. **可中断指令执行** — 中途更改语言指令会使过期动作块失效；
4. **失败感知恢复** — 空抓/超时检测，并允许一次确定性重试；
5. **安全监视器** — 进入仿真前的关节限幅与速率限制；
6. **单卡 ROCm 路径** — 在 AMD Radeon 上完成仿真、数据、训练、推理与评测；
7. **多目标部分完成指标** — 按层级成功率与部分完成率统计长时序任务。
8. **可重复压力测试** — 确定性移动目标水果/盘位，并支持 baseline 与 Reflex 消融；
9. **可审阅证据** — 自动输出 JSON、CSV、摘要、真实 checkpoint 哈希和带实时状态的视频；
10. **中断安全采集** — 未完成数据只保留在 staging，不会覆盖上一份有效数据。

> 状态：流水线代码已就绪。AMD 实测结果、训练权重、正式指标、技术报告 PDF 与演示视频
> 将在远程 Radeon 环境跑完后补齐。

本目录为完整、自包含的提交单元。从比赛仓库根目录进入
`track3_VisioBotLab_RadeonVLA-Reflex/`，按本文档即可复现。

## 提交信息

| 字段 | 内容 |
|---|---|
| 赛道 | Track 3 — Physical AI Challenge |
| 团队 | VisioBot Lab |
| 项目 | RadeonVLA-Reflex |
| 成员 | Zhenwei Zhou |
| 单位 | 南京理工大学 |

## 目标应用

目标应用为食品处理、实验室自动化与小批量物流中的语言可重配置分拣单元。
操作员可以在机器人运动途中修改目标；运行层立即作废旧动作块、进入安全张爪保持，
并能对检测到的空抓执行一次恢复重试。

### 任务层级

| 层级 | 名称 | 策略需要完成的内容 | 示例 |
|---|---|---|---|
| **L1** | 基础命名 | 水果 × 碗（5 种水果 × 4 个碗） | `banana_white_left`、`apple_blue_left`、`orange_blue_right` |
| **L2** | 空间指代 | 随机化后解析 *最左/最右/最近/最远* | `leftmost_to_white_left`、`leftmost_to_blue_left` |
| **L3** | 多步序列 | 同一局内完成**有序**多物体放置 | `seq_banana_white_left_lemon_white_right`、`seq_apple_blue_left_orange_blue_right` |
| **L4** | 属性规则 | 将颜色/形状规则展开为多个子目标 | `rule_yellow_white_left_purple_white_right`、`rule_red_blue_left_orange_blue_right` |

场景物体：**香蕉、柠檬、李子、苹果、橙子**，以及 **四个正放固定碗** —
**左侧白+蓝，右侧白+蓝**（均可放置水果）。

套件（CLI `--suite`）：

| 套件 | 内容 |
|---|---|
| `basic` | 仅 L1（20 个任务） |
| `spatial` | L2 |
| `multistep` | L3 |
| `rules` | L4 |
| `advanced` | L2+L3+L4 |
| `full` | 全部层级（显式启用的高级基准） |

训练与评测使用**不相交**的自然语言表述。空间与规则任务在位姿随机化后，
由 `radeonvla.grounding` 在 episode 开始时解析。

## 系统架构

```text
自然语言指令 ───────────────────────┐
世界相机 RGB ───────────────────────┤
腕部相机 RGB ───────────────────────┤
机器人与夹爪状态 ───────────────────┤
                                    ↓
                          SmolVLA 策略
                                    ↓
                              动作块
                                    ↓
                         执行安全监视器
                         ├─ 关节限幅 / 速率限制
                         ├─ 指令版本变更
                         ├─ 空抓检测
                         ├─ 超时 + 一次恢复重试
                         └─ 事件 / 延迟遥测
                                    ↓
                    Genesis Franka 双碗仿真
                                    ↓
                              下一帧观测
```

学习栈为语言与视觉条件下的端到端关节位置控制。
指令作废与恢复为策略外的确定性安全层（不重新训练 VLA）。评测可确定性注入水果或盘位
移动，并把 `RUNNING / INTERRUPTED / RECOVERING / SUCCESS` 直接叠加到演示视频。

## 仓库结构

```text
track3_VisioBotLab_RadeonVLA-Reflex/
├── README.md                 # 英文（正式提交）
├── README.zh-CN.md           # 中文说明
├── pyproject.toml
├── environment.local.yml
├── requirements.local.txt
├── requirements.remote.txt
├── configs/
│   ├── base.yaml
│   ├── train.yaml
│   └── eval.yaml
├── src/radeonvla/
│   ├── scene.py              # Genesis 双碗场景
│   ├── expert.py             # 脚本分拣专家
│   ├── record_dataset.py     # LeRobot 数据采集（训练前置）
│   ├── validate_dataset.py   # 训练前数据集检查
│   ├── train_policy.py       # SmolVLA / ACT 训练封装
│   ├── evaluate.py           # 闭环评测 + 中断 + 恢复
│   ├── safety.py             # 指令会话、安全与失败处理
│   ├── pipeline.py           # 阶段编排 / all-smoke
│   ├── benchmark.py          # 吞吐 / 延迟
│   ├── setup_assets.py       # 填充机器人/YCB 资产
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

数据集、权重、生成视频、实验输出、凭证与私有配置不纳入 Git。

## 依赖策略

PyTorch 需按执行平台单独安装，不与项目其余依赖混装：

- 已验证的本地开发环境使用 CPU 版 PyTorch（导入与单测）；
- 比赛环境须使用与 ROCm 版本匹配的 PyTorch HIP 构建；
- `pyproject.toml` 中故意不写通用 PyPI `torch` 依赖；
- 安装其余依赖时不得覆盖已验证的 PyTorch 构建。

核心版本：

| 组件 | 版本 |
|---|---|
| Python | 3.12 |
| PyTorch（本地） | 2.9.1+cpu |
| torchvision（本地） | 0.24.1+cpu |
| torchaudio（本地） | 2.9.1+cpu |
| Genesis | 1.1.2 |
| LeRobot | 0.6.0 |

Track 3 starter 文档中给出了 ROCm 7.2.1 专用 wheel 集合。仅当远程实例报告
ROCm 7.2.1 且 Python 3.12 时使用该集合；否则在安装 `requirements.remote.txt`
前先选择匹配的官方 ROCm 轮子。

## 仿真资产（复现必需）

网格资产已**纳入本仓库**的 `assets/`（约 42 MB）。评委 `git clone` 后即可运行，
无需额外私有网盘。

| 路径 | 内容 |
|---|---|
| `assets/ycb/011_banana`、`013_apple`、`014_lemon`、`017_orange`、`018_plum`、`024_bowl` | YCB 网格 |
| `assets/robots/franka/` | Franka Emika Panda MJCF |
| `assets/SHA256SUMS` | 完整性校验 |

```bash
python -m radeonvla.setup_assets           # 已存在则跳过
python -m radeonvla.setup_assets --verify  # 校验 SHA256
python -m radeonvla.setup_assets --download # 缺失时的可选网络回退
```

来源与说明：[`assets/README.md`](assets/README.md)、[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

- YCB Object and Model Set：https://www.ycbbenchmarks.com/object-models/
- YCB 数据门户：http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/
- Genesis（Franka 也可从已安装的 genesis 包恢复）：https://github.com/Genesis-Embodied-AI/Genesis

## 本地开发环境

已验证的本地开发机为 Ubuntu 22.04.5（联想拯救者 R7000 2021，Ryzen 5 5600H，
16 GB 内存，NVIDIA RTX 3050）。该机器为开发客户端，**不是**最终 AMD 执行机。

### 重建 Conda 环境

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

### 校验本地环境

```bash
conda activate radeonvla-dev
python -m radeonvla.check_env --json docs/environment.local.json
python -m radeonvla.setup_assets
pytest
ruff check src tests
python -m radeonvla.submission_audit
```

本地结果不能作为 Radeon / ROCm 执行证据。

## 远程 AMD Radeon 环境

使用带持久 PVC 的 Radeon Cloud 实例，并只暴露一张 GPU。
ROCm 轮子细节见 `docs/REMOTE_ROCM_SETUP.md`。

### 1. 审计未改动的实例

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

### 2. 克隆到持久卷

```bash
cd /workspace
mkdir -p visiobot
cd visiobot
git clone https://github.com/zzw-rgb/Radeon-hackathon-2026-07.git
cd Radeon-hackathon-2026-07
git checkout submission/track3-visiobotlab-radeonvla-reflex
cd track3_VisioBotLab_RadeonVLA-Reflex
```

### 3. 创建或复用 Python 3.12 环境

若镜像已在 Python 3.12 中提供验证过的 PyTorch HIP 构建：

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

### 4. 安装其余依赖

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

### 5. 严格 AMD 校验

```bash
export HIP_VISIBLE_DEVICES=0
bash scripts/check_remote_amd.sh
```

## 端到端流水线（已实现）

以下阶段均以 `python -m radeonvla.<module>` 入口提供。

| 阶段 | 模块 | 作用 |
|---|---|---|
| 资产 | `setup_assets` | 将 Franka + YCB 网格放入 `assets/` |
| 环境检查 | `check_env` | Torch / HIP / Genesis 报告 |
| 场景 | `scene` | 双碗 Genesis 冒烟与可选截图 |
| 专家 | `expert` | 语言条件下的脚本抓取放置 |
| **采集** | **`record_dataset`** | **采集 LeRobot 演示（训练前置）** |
| 校验 | `validate_dataset` | 训练前 schema / NaN / 图像检查 |
| 训练 | `train_policy` | 经 `lerobot-train` 训练 SmolVLA / ACT |
| 评测 | `evaluate` | 闭环策略 + 中断 + 恢复 |
| 基准 | `benchmark` | 仿真吞吐 / 可选推理延迟 |
| 编排 | `pipeline` | 阶段编排（`all-smoke` 等） |

### 一键脚本（推荐）

| 脚本 / Make 目标 | 作用 |
|---|---|
| `bash scripts/run_all_local.sh` / `make all-local` | 本地一键：资产→场景→专家→**采集**→校验 |
| `bash scripts/run_record.sh` / `make record-local` | 仅采集（可用 `EPISODES`、`SUITE`、`BACKEND`） |
| `bash scripts/run_expert_demo.sh` / `make expert-demo` | 脚本专家演示（基础/困难混合） |
| `bash scripts/run_pipeline_smoke.sh` / `make smoke` | 1 episode 冒烟 + 训练 dry-run |
| `bash scripts/run_full_remote.sh` / `make remote-full` | AMD 全流程：检查→采集→训练→评测→基准 |
| `bash scripts/check_local.sh` / `make check` | 环境 + 审计 + pytest + ruff |
| `bash scripts/check_remote_amd.sh` / `make remote-check` | 严格 ROCm 门禁 |

```bash
# 本地：采集 10 条 basic episode
EPISODES=10 SUITE=basic bash scripts/run_record.sh

# 本地：一键流水线
EPISODES=5 bash scripts/run_all_local.sh

# 快速冒烟
make smoke

# AMD Radeon
EPISODES=200 SUITE=basic bash scripts/run_full_remote.sh
```

变量说明见 [`scripts/README.md`](scripts/README.md)。可选从 `.env.example` 复制 `.env`。

### 模块形式的本地冒烟

```bash
bash scripts/run_pipeline_smoke.sh
# 等价：
python -m radeonvla.pipeline all-smoke --backend cpu --episodes 1 --task banana_white_left
```

执行顺序：资产 → 环境 → 场景 → 专家(1) → **采集(1)** → 校验 → 训练 dry-run。

### 分步命令

```bash
# 环境与资产
python -m radeonvla.check_env
python -m radeonvla.check_env --require-amd --init-genesis
python -m radeonvla.setup_assets
python -m radeonvla.submission_audit

# M1 — 场景冒烟
python -m radeonvla.scene --backend cpu --steps 100 --save-frames
python -m radeonvla.scene --backend amdgpu --steps 100 --save-frames

# M2 — 脚本专家（基础 + 多步）
python -m radeonvla.expert --task banana_white_left --episodes 5 --backend cpu
python -m radeonvla.expert --task seq_triple_sort --episodes 3 --backend cpu
python -m radeonvla.expert --suite advanced --episodes 8 --backend amdgpu

# M3 — 主基准数据采集（20 个 L1 任务，每项至少 10 个成功示范）
python -m radeonvla.record_dataset \
  --episodes 200 \
  --suite basic \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --backend amdgpu \
  --require-coverage

# 仅在新数据完成验证后安全替换旧数据
python -m radeonvla.record_dataset --episodes 200 --suite basic --require-coverage \
  --overwrite --discard-incomplete \
  --repo-id visiobot/radeonvla_basic --dataset-root datasets/radeonvla_basic

# 采集时可选域随机
python -m radeonvla.record_dataset --episodes 400 --suite basic --require-coverage \
  --dr-appearance --dr-object-color --dr-runtime --backend amdgpu

# 正式纯物理数据：20 个任务，每个恰好 50 条成功 episode。
# 默认关闭运动学粘附、物体瞬移和 placement nudge，并为每条数据写原子证书。
SOURCE_COMMIT="$(git rev-parse HEAD)" python -m radeonvla.record_dataset \
  --episodes-per-task 50 --suite basic --require-coverage \
  --repo-id YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --dr-appearance --dr-object-color --dr-runtime --dr-rebuild-every 20 \
  --max-attempts 10000 --backend amdgpu

# 中断后续采；参数和源码 revision 必须与原子进度记录一致。
SOURCE_COMMIT="$(git rev-parse HEAD)" python -m radeonvla.record_dataset \
  --episodes-per-task 50 --suite basic --require-coverage \
  --repo-id YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --dr-appearance --dr-object-color --dr-runtime --dr-rebuild-every 20 \
  --max-attempts 10000 --backend amdgpu --resume-incomplete

# 训练前校验数据集
python -m radeonvla.validate_dataset \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex

# 正式发布门禁
python -m radeonvla.validate_dataset \
  --repo-id YOUR_HF_NAMESPACE/radeonvla-reflex-physical-1k \
  --dataset-root datasets/radeonvla_reflex_physical_1k \
  --expected-episodes 1000 --episodes-per-task 50 --require-strict-physics

# M4/M5 — 训练 SmolVLA（需要非空数据集）
python -m radeonvla.train_policy smolvla \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --steps 10000 --device cuda

# 闭环评测（中断 + 恢复）
python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex/checkpoints/last/pretrained_model \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --episodes-per-task 10 --save-video --backend amdgpu

# 可中断性演示（在第 0 局中途注入指令变更）
python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex/checkpoints/last/pretrained_model \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --interrupt-demo --save-video --backend amdgpu

# 吞吐 / 延迟
python -m radeonvla.benchmark --backend amdgpu --steps 500
```

### 远程全流程脚本（AMD）

```bash
export HIP_VISIBLE_DEVICES=0
bash scripts/run_full_remote.sh
# 或自定义：
EPISODES=200 SUITE=basic TRAIN_STEPS=10000 bash scripts/run_full_remote.sh
```

自包含 Docker（Track 3 推荐）：

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

docker compose -f docker/compose.yaml run --rm radeonvla check-amd
```

源码、配置、脚本、资产和测试已经包含在镜像内，仅挂载可变的数据、权重和结果。
入口命令包括 `help`、`check-amd`、`smoke`、`remote-full`、`reflex-demo` 和 `shell`。

## 数据规格

每帧包含：

```text
observation.images.world   # HWC uint8 RGB
observation.images.wrist   # HWC uint8 RGB
observation.state          # 9 维 qpos（7 臂 + 2 指）
action                     # 9 维绝对关节位置目标
task                       # 自然语言指令
```

| 项 | 值 |
|---|---|
| 动作类型 | 绝对关节位置 |
| 维度 | 9 |
| 关节顺序 | panda_joint1..7, panda_finger_joint1..2 |
| 夹爪范围 | [0.0, 0.04] m |
| 控制 / 数据集帧率 | 20 Hz（仿真 100 Hz，降采样） |
| 图像尺寸 | 320×240 |

种子划分：

| 划分 | 种子 |
|---|---|
| 训练 | 0–9999 |
| 验证 | 10000–10999 |
| 正式评测 | 20000–29999 |
| 中断 / 恢复 | 30000–30999 |

## 评测协议

主协议为 20 个 L1 任务各 10 个 held-out episode，共 200 个。中断和目标移动
压力测试使用代表性任务与独立 seed；L2–L4 只有在实际训练评测后才报告。

报告指标：

- 任务成功率；
- 物体正确率；
- 目标正确率；
- 首次尝试成功；
- 允许恢复后的最终成功；
- 恢复成功；
- 安全中断率与指令到动作作废的步数；
- 按任务和扰动场景统计的成功率；
- 完成时间均值与 P95；
- 推理延迟 P50 与 P95；
- 仿真步每秒；
- 训练样本每秒；
- 训练与推理峰值显存。

包括失败在内的每个 episode 均保留在 JSON 中。正式证据自动写入
`artifacts/evaluation.json`、`evaluation.csv` 和 `summary.md`，模式为
`artifacts/evaluation.schema.json`。视频会显示当前指令、Reflex 状态、版本、重试和延迟。

## 复现步骤

1. 在提交 commit 克隆仓库；
2. 配置匹配的 ROCm/PyTorch 环境；
3. 安装项目依赖（`requirements.remote.txt` + `pip install -e .`）；
4. 运行 `python -m radeonvla.setup_assets`（或按文档提供资产）；
5. 运行严格 AMD 环境校验；
6. 对 Genesis 场景做冒烟测试；
7. 采集演示数据或下载公开数据集修订；
8. 训练或下载公开 SmolVLA 权重；
9. 运行 held-out 评测并写出 JSON 与视频；
10. 将生成元数据与技术报告对照。

最终发布修订不应依赖私有账号、未公开文件或额外改源码。

## 交付物

| 交付物 | 状态 | 链接 |
|---|---|---|
| 源代码 | 流水线已实现 | 本自包含目录 |
| 可复现 README | 本文件 / 英文版 | README.md |
| 技术报告（MD） | 草稿结构 | reports/RadeonVLA-Reflex-Technical-Report.md |
| 技术报告 PDF | 最终指标确定后导出 | `reports/RadeonVLA-Reflex-Technical-Report.pdf` |
| 演示视频 | 用最终 checkpoint 生成 | `outputs/eval_videos/` |
| 模型权重 | 选择最新且验证通过的数字 checkpoint | `outputs/train/*/checkpoints/*/pretrained_model` |
| 数据集或数据文档 | 模板 | docs/DATASET_CARD.md |
| 原始评测结果 | 由远程流程生成 | `artifacts/evaluation.json` |
| SHA256 校验和 | 由远程流程生成 | `artifacts/SHA256SUMS` |
| Docker 镜像定义 | 可用 | docker/Dockerfile |

提交撰写相关文件：

- `docs/DATASET_CARD.md`
- `docs/MODEL_CARD.md`
- `reports/RadeonVLA-Reflex-Technical-Report.md`

```bash
python -m radeonvla.submission_audit
python -m radeonvla.submission_audit --final   # PDF 与 checksum 齐备前会失败
```

## 参考与致谢

- AMD Track 3 比赛仓库
- AMD Radeon Cloud 用户指南
- Track 3 Franka fruit-pick demo（Genesis + LeRobot on ROCm 流程参考）
- Genesis World
- Hugging Face LeRobot / SmolVLA
- YCB Object and Model Set

上游参考仓库在本提交目录外维护。本树为 RadeonVLA-Reflex 项目代码；
依赖声明见 `THIRD_PARTY_NOTICES.md`。

## 团队

- Zhenwei Zhou — 系统设计、实现、训练、评测与提交
- VisioBot Lab
- 南京理工大学

## 提交

官方 Pull Request 标题：

```text
Track 3, VisioBot Lab, RadeonVLA-Reflex
```

所有提交材料、项目说明与 Pull Request 正文使用英文。
