# RadeonVLA-Reflex（中文说明）

> **语言：** 中文辅助说明。正式比赛提交材料以英文为准，请同时阅读 [README.md](README.md)。  
> 官方要求：PR 与提交说明使用 **English**。

RadeonVLA-Reflex 是我（Zhenwei Zhou / VisioBot Lab）参加 AMD AI DevMaster Hackathon
**Track 3（Physical AI）** 的提交项目。目标是在 Genesis 中用 Franka Panda + **SmolVLA**
完成**语言引导的双碗水果分拣**，并在 AMD Radeon / ROCm 上跑通仿真、采集、训练与评测。

本仓库的设计重点：

1. **分级任务套件 L1–L4**
   - L1 基础命名：水果 × 左右碗
   - L2 **空间指代**：leftmost / rightmost / nearest / farthest（随机化后才确定对象）
   - L3 **多步长时序**：一局完成多个有序放置（如 banana→左，lemon→右）
   - L4 **属性规则**：黄→左、紫→右；弯→左、圆→右
2. **可中断指令**：中途改语言命令会作废旧 action chunk
3. **失败感知恢复**：空抓 / 超时 + 一次重试
4. **安全监视器**：关节限幅与速率限制
5. **分层指标**：按 tier 成功率 + multi-goal 部分完成率
6. **单卡 ROCm 全链路**

---

## 提交信息

| 字段 | 内容 |
|---|---|
| Track | Track 3 — Physical AI |
| 团队 | VisioBot Lab |
| 项目 | RadeonVLA-Reflex |
| 成员 | Zhenwei Zhou |
| 单位 | 南京理工大学 |

PR 标题建议：

```text
Track 3, VisioBot Lab, RadeonVLA-Reflex
```

---

## 完整流程是否已实现？

**是。** 训练前必须先跑数据采集。对应模块：

| 阶段 | 命令 | 说明 |
|---|---|---|
| 资产 | `python -m radeonvla.setup_assets` | 准备 Franka / YCB 网格 |
| 环境 | `python -m radeonvla.check_env` | 检查 torch / HIP / Genesis |
| 场景 | `python -m radeonvla.scene` | 双碗场景冒烟 |
| 专家 | `python -m radeonvla.expert` | 脚本抓取放置 |
| **采集** | **`python -m radeonvla.record_dataset`** | **写入 LeRobot 数据集（训练前置）** |
| 校验 | `python -m radeonvla.validate_dataset` | 检查维度 / 黑图 / NaN |
| 训练 | `python -m radeonvla.train_policy smolvla` | 微调 SmolVLA |
| 评测 | `python -m radeonvla.evaluate` | 闭环 + 中断 + 恢复 |
| 基准 | `python -m radeonvla.benchmark` | 吞吐 / 延迟 |
| 编排 | `python -m radeonvla.pipeline all-smoke` | 一键冒烟 |

本地已验证：`record_dataset` 可成功录制 1 个 `banana_left` episode（约 164 帧）并写出 dataset。

---

## 一键脚本（本机 / 远程）

```bash
cd track3_VisioBotLab_RadeonVLA-Reflex
conda activate radeonvla-dev   # 或你的环境

# 本机采集 10 条
EPISODES=10 SUITE=basic bash scripts/run_record.sh

# 本机一键：场景 + 专家 + 采集 + 校验
EPISODES=5 bash scripts/run_all_local.sh

# 快速冒烟（1 条）
make smoke

# 远程 AMD 全流程
EPISODES=100 SUITE=full bash scripts/run_full_remote.sh
```

更多变量说明见 `scripts/README.md`；可复制 `.env.example` 为 `.env`。

---

## 训练前必做：数据采集

```bash
# 小规模试跑
python -m radeonvla.record_dataset \
  --episodes 5 \
  --task banana_left \
  --backend cpu \
  --repo-id visiobot/radeonvla_reflex_smoke \
  --dataset-root datasets/radeonvla_reflex_smoke \
  --overwrite

# 正式采集（建议远程 AMD GPU）
python -m radeonvla.record_dataset \
  --episodes 100 \
  --backend amdgpu \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --overwrite \
  --dr-appearance --dr-object-color --dr-runtime

# 训练前校验
python -m radeonvla.validate_dataset \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex
```

数据集每帧包含：

- `observation.images.world` / `wrist`（320×240 RGB）
- `observation.state`（9 维关节）
- `action`（9 维绝对关节目标）
- `task`（自然语言指令，训练用措辞）

---

## 训练与评测

```bash
python -m radeonvla.train_policy smolvla \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --steps 10000 --device cuda

python -m radeonvla.evaluate \
  --policy-path outputs/train/smolvla_radeonvla_reflex/checkpoints/last/pretrained_model \
  --repo-id visiobot/radeonvla_reflex \
  --dataset-root datasets/radeonvla_reflex \
  --episodes-per-task 10 --save-video --backend amdgpu

# 中途改指令 demo
python -m radeonvla.evaluate ... --interrupt-demo --save-video
```

远程一键：

```bash
export HIP_VISIBLE_DEVICES=0
bash scripts/run_full_remote.sh
```

---

## 任务套件

| suite | 内容 |
|---|---|
| `basic` | 仅 L1（6 个） |
| `spatial` | L2 空间指代 |
| `multistep` | L3 多步序列 |
| `rules` | L4 属性规则 |
| `advanced` | L2+L3+L4 |
| **`full`** | **全部（默认采集/评测）** |

示例：

```bash
python -m radeonvla.expert --task seq_triple_sort --episodes 2
python -m radeonvla.expert --task leftmost_to_left --episodes 3
python -m radeonvla.record_dataset --suite full --episodes 100 --overwrite
python -m radeonvla.record_dataset --suite multistep --episodes 40 --overwrite
```

训练 / 评测指令分离，见 `src/radeonvla/tasks.py` 与 `src/radeonvla/grounding.py`。

---

## 环境依赖要点

- Python 3.12
- PyTorch **按平台单独安装**（本地 CPU 或 ROCm HIP 轮子），不要装错 torch
- `genesis-world==1.1.2`、`lerobot[training,smolvla]==0.6.0`
- 视频解码默认 **pyav**（避免 torchcodec / FFmpeg 版本问题）

详细英文环境步骤见 [README.md](README.md)。

---

## 仓库结构（节选）

```text
track3_VisioBotLab_RadeonVLA-Reflex/
├── README.md              # 英文（比赛正式版）
├── README.zh-CN.md        # 中文（本文件）
├── configs/
├── src/radeonvla/
│   ├── record_dataset.py  # 数据采集
│   ├── train_policy.py
│   ├── evaluate.py
│   ├── safety.py          # 中断 / 恢复 / 安全
│   └── pipeline.py
├── scripts/
│   ├── run_pipeline_smoke.sh
│   └── run_full_remote.sh
├── docs/ reports/ docker/
└── assets/README.md       # 大文件需 setup_assets 填充
```

本地草稿目录不会进入 Git 提交。

---

## 交付物清单

| 交付物 | 状态 |
|---|---|
| 源码 + 可复现 README | 已具备 |
| 中英文 README | 已具备 |
| 技术报告 MD | 结构已有，实测数字待我在远程 AMD 上跑完后填写 |
| 数据集 / checkpoint / 视频 / PDF | 待远程 AMD 跑完后补齐 |

---

## 团队

- Zhenwei Zhou — 系统设计、实现、训练、评测与提交  
- VisioBot Lab · 南京理工大学  

环境安装、评测协议与复现步骤以英文 [README.md](README.md) 为准。
