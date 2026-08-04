export type Locale = "en" | "zh";

type LocalizedText = Record<Locale, string>;

export interface Metric {
  value: string;
  label: LocalizedText;
  detail: LocalizedText;
  status?: "verified" | "pending";
}

export interface Demo {
  index: string;
  state: string;
  title: LocalizedText;
  body: LocalizedText;
  event: LocalizedText;
}

export interface Feature {
  eyebrow: string;
  title: LocalizedText;
  body: LocalizedText;
}

export interface TaskRow {
  fruit: LocalizedText;
  targets: Array<{ label: LocalizedText; color: "white" | "blue" }>;
}

export const projectLinks = {
  source:
    "https://github.com/zzw-rgb/Radeon-hackathon-2026-07/tree/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex",
  contest: "https://modelscope.cn/events/299/比赛介绍",
  baseModel: "https://huggingface.co/lerobot/smolvla_base",
};

export const navItems: Array<{ href: string; label: LocalizedText }> = [
  { href: "#demo", label: { en: "Evidence", zh: "演示证据" } },
  { href: "#runtime", label: { en: "Runtime", zh: "运行机制" } },
  { href: "#benchmark", label: { en: "Benchmark", zh: "基准" } },
  { href: "#reproduce", label: { en: "Reproduce", zh: "复现" } },
];

export const copy = {
  pageTitle: { en: "RadeonVLA-Reflex · VisioBot Lab", zh: "RadeonVLA-Reflex · VisioBot Lab 项目展示" },
  pageDescription: {
    en: "RadeonVLA-Reflex — an interruptible and recoverable VLA runtime for language-guided robotic sorting on AMD Radeon.",
    zh: "RadeonVLA-Reflex：运行在 AMD Radeon 上、面向语言引导机器人分拣的可中断、可恢复 VLA 执行层。",
  },
  skipLink: { en: "Skip to project overview", zh: "跳到项目概览" },
  primaryNav: { en: "Primary navigation", zh: "主导航" },
  homeLabel: { en: "RadeonVLA-Reflex home", zh: "RadeonVLA-Reflex 首页" },
  brandKicker: { en: "VISIOBOT LAB · TRACK 3", zh: "VISIOBOT LAB · 赛道 3" },
  languageLabel: { en: "Language", zh: "语言" },
  heroBadge: {
    en: "Physical AI Challenge · Simulation",
    zh: "Physical AI 挑战赛 · 仿真项目",
  },
  heroTitleA: { en: "Actions that can", zh: "让机器人动作" },
  heroTitleB: { en: "change their mind.", zh: "随指令及时改变。" },
  heroBody: {
    en: "RadeonVLA-Reflex wraps a vision-language-action policy with command invalidation, safe interruption, and one-shot recovery—so stale action chunks do not stay in control.",
    zh: "RadeonVLA-Reflex 在视觉语言动作策略外加入指令失效、安全中断与单次恢复机制，避免过期动作块继续控制机械臂。",
  },
  sourceCta: { en: "Explore the source", zh: "查看项目源码" },
  demoCta: { en: "See the evidence plan", zh: "查看演示证据" },
  heroAlt: {
    en: "Industrial robot holding an apple while a broken stale action path is rerouted to a safe recovery path",
    zh: "工业机械臂夹持苹果，失效的旧动作路径断开并重新规划为安全恢复路径",
  },
  placeholder: { en: "Original recovery concept art", zh: "原创恢复机制概念图" },
  proofLabel: { en: "Verified snapshot", zh: "已核验快照" },
  proofNote: {
    en: "Values below come from the completed local dataset manifest. Formal policy metrics remain pending.",
    zh: "下列数字来自已完成的数据集 manifest；正式策略指标仍待最终评测。",
  },
  sectionDemoKicker: { en: "JUDGE-FACING STORY", zh: "面向评委的故事线" },
  sectionDemoTitle: {
    en: "Three moments. One execution layer.",
    zh: "三个关键时刻，一套执行层。",
  },
  sectionDemoBody: {
    en: "The final narrated video will show the same checkpoint under normal execution, a mid-command change, and a deterministic target shift. Media is intentionally not fabricated before those runs pass.",
    zh: "最终解说视频将使用同一 checkpoint，展示正常执行、中途改指令和确定性目标扰动。正式实跑通过前，本站不会使用伪造媒体。",
  },
  videoLabel: { en: "3+ MIN NARRATED WALKTHROUGH", zh: "3 分钟以上解说视频" },
  videoPending: { en: "Pending final evaluation recordings", zh: "等待最终评测录制" },
  videoBody: {
    en: "The player will be connected after the final Radeon run, with captions and a direct download fallback.",
    zh: "最终 Radeon 实跑完成后接入播放器，并提供字幕与直接下载备用链接。",
  },
  plannedEvidence: { en: "Planned evidence", zh: "计划展示" },
  runtimeKicker: { en: "WHY REFLEX", zh: "为什么需要 REFLEX" },
  runtimeTitle: { en: "The policy proposes. The runtime decides.", zh: "策略提出动作，运行层决定是否执行。" },
  runtimeBody: {
    en: "Action chunking improves throughput, but an old chunk can outlive the instruction that created it. Reflex adds a deterministic boundary between learned control and the simulator.",
    zh: "动作分块可以提升吞吐，但旧动作块可能比生成它的指令活得更久。Reflex 在学习控制与仿真器之间加入确定性边界。",
  },
  architectureLabel: { en: "Execution path", zh: "执行路径" },
  architectureInput: { en: "Language + RGB + state", zh: "语言 + RGB + 状态" },
  architecturePolicy: { en: "SmolVLA policy", zh: "SmolVLA 策略" },
  architectureReflex: { en: "Reflex runtime", zh: "Reflex 运行层" },
  architectureSafety: { en: "invalidate · clamp · retry", zh: "失效 · 限幅 · 重试" },
  architectureSim: { en: "Genesis + Franka", zh: "Genesis + Franka" },
  benchmarkKicker: { en: "PRIMARY BENCHMARK", zh: "主要基准" },
  benchmarkTitle: { en: "Five fruits. Four destinations. Twenty tasks.", zh: "五种水果，四个盘位，二十项任务。" },
  benchmarkBody: {
    en: "The L1 suite crosses every fruit with every language-addressable bowl position. Each row currently contains 10 completed expert demonstrations.",
    zh: "L1 套件将每种水果与每个可由语言指定的盘位组合。当前每个组合包含 10 条已完成专家演示。",
  },
  targetLabel: { en: "Destination", zh: "目标盘位" },
  objectLabel: { en: "Object", zh: "物体" },
  demosLabel: { en: "10 demos", zh: "10 条演示" },
  evidenceKicker: { en: "NO PLACEHOLDER CLAIMS", zh: "不使用占位成绩" },
  evidenceTitle: { en: "Measured results, or a clear Pending.", zh: "只展示实测结果，否则明确标记待完成。" },
  evidenceBody: {
    en: "The initial dataset proves the recording and training path, not policy success. Final success, latency, memory, and Reflex ablations will be published from immutable evaluation artifacts.",
    zh: "初始数据集证明采集与训练链路可运行，但不等于策略成功。最终成功率、延迟、显存和 Reflex 消融将从不可变评测产物中发布。",
  },
  resultLabels: [
    { en: "Final policy success", zh: "最终策略成功率" },
    { en: "P95 inference latency", zh: "P95 推理延迟" },
    { en: "Baseline vs Reflex", zh: "Baseline 与 Reflex 对照" },
    { en: "Final checkpoint", zh: "最终 checkpoint" },
  ],
  pending: { en: "Pending", zh: "待完成" },
  resultPendingNote: {
    en: "Filled only after held-out evaluation on the final checkpoint.",
    zh: "仅在最终 checkpoint 完成独立评测后填写。",
  },
  releaseTarget: { en: "Next release target", zh: "下一版本目标" },
  releaseTargetValue: { en: "1,000 demos · 20 × 50", zh: "1,000 条演示 · 20 × 50" },
  releaseTargetBody: {
    en: "A balanced expert dataset with a separate validation seed range. This is a target—not a completed result.",
    zh: "均衡专家数据集，并使用独立验证 seed 范围。这是目标，不是已完成成绩。",
  },
  modelLabel: { en: "Base policy", zh: "基础策略" },
  modelValue: { en: "LeRobot / SmolVLA", zh: "LeRobot / SmolVLA" },
  modelBody: {
    en: "Fine-tuned for 9-D absolute joint-position control from two RGB views and language.",
    zh: "使用双路 RGB 与语言输入，微调为 9 维绝对关节位置控制。",
  },
  baseModelCta: { en: "Open base model", zh: "查看基础模型" },
  reproduceKicker: { en: "REVIEWABLE BY DESIGN", zh: "为可审阅而设计" },
  reproduceTitle: { en: "From command to checksum.", zh: "从指令到校验和，全链路可审阅。" },
  reproduceBody: {
    en: "The repository separates source, datasets, checkpoints, and small evidence artifacts. Evaluation emits JSON, CSV, Markdown summaries, videos, and a deterministic checkpoint hash.",
    zh: "仓库将源码、数据、权重和小型证据产物分离。评测会输出 JSON、CSV、Markdown 摘要、视频与确定性 checkpoint 哈希。",
  },
  pipelineSteps: [
    { en: "Validate AMD / ROCm environment", zh: "校验 AMD / ROCm 环境" },
    { en: "Record and validate demonstrations", zh: "采集并验证专家演示" },
    { en: "Fine-tune on one visible GPU", zh: "在单张可见 GPU 上微调" },
    { en: "Run held-out and stress evaluations", zh: "运行独立评测与压力测试" },
    { en: "Publish artifacts, hashes, and video", zh: "发布产物、哈希与视频" },
  ],
  commandLabel: { en: "Reproduce the local checks", zh: "复现本地检查" },
  limitationLabel: { en: "Scope", zh: "适用范围" },
  limitationBody: {
    en: "Simulation-only. RadeonVLA-Reflex does not claim real-robot transfer. Object, language, and camera coverage are limited to the submitted Genesis benchmark.",
    zh: "当前仅限仿真。RadeonVLA-Reflex 不声称可直接迁移到真实机械臂；物体、语言和相机覆盖限于提交的 Genesis 基准。",
  },
  teamKicker: { en: "TEAM", zh: "团队" },
  teamTitle: { en: "VisioBot Lab", zh: "VisioBot Lab" },
  teamBody: {
    en: "Zhenwei Zhou · Nanjing University of Science and Technology",
    zh: "周振威 · 南京理工大学",
  },
  contestCta: { en: "Competition page", zh: "比赛页面" },
  footer: {
    en: "RadeonVLA-Reflex · Track 3 Physical AI Challenge",
    zh: "RadeonVLA-Reflex · Track 3 Physical AI 挑战赛",
  },
  attribution: {
    en: "Hero concept art generated for RadeonVLA-Reflex. Third-party software and simulation credits are listed in THIRD_PARTY_NOTICES.md.",
    zh: "Hero 概念图为 RadeonVLA-Reflex 项目生成；第三方软件与仿真署名详见 THIRD_PARTY_NOTICES.md。",
  },
} satisfies Record<string, unknown>;

export const verifiedMetrics: Metric[] = [
  {
    value: "200",
    label: { en: "expert demonstrations", zh: "条专家演示" },
    detail: { en: "manifest status: complete", zh: "manifest 状态：complete" },
  },
  {
    value: "20 / 20",
    label: { en: "L1 tasks covered", zh: "L1 任务已覆盖" },
    detail: { en: "10 episodes per task", zh: "每项任务 10 条" },
  },
  {
    value: "46,420",
    label: { en: "recorded frames", zh: "帧已录制" },
    detail: { en: "at 20 Hz", zh: "采样频率 20 Hz" },
  },
  {
    value: "2",
    label: { en: "RGB camera views", zh: "路 RGB 相机" },
    detail: { en: "world + wrist", zh: "世界视角 + 腕部视角" },
  },
];

export const demos: Demo[] = [
  {
    index: "01",
    state: "RUNNING",
    title: { en: "Normal execution", zh: "正常执行" },
    body: {
      en: "Language and two RGB observations condition the policy while the safety monitor checks every action.",
      zh: "语言与双路 RGB 观测共同驱动策略，安全监视器检查每一步动作。",
    },
    event: { en: "command v1 · action chunk active", zh: "指令 v1 · 动作块执行中" },
  },
  {
    index: "02",
    state: "INTERRUPTED",
    title: { en: "Mid-command change", zh: "中途改变指令" },
    body: {
      en: "A new command increments the session version. Stale actions are invalidated and the gripper enters a safe hold.",
      zh: "新指令使会话版本递增；过期动作立即失效，夹爪进入安全保持。",
    },
    event: { en: "v1 → v2 · stale chunk dropped", zh: "v1 → v2 · 丢弃过期动作块" },
  },
  {
    index: "03",
    state: "RECOVERING",
    title: { en: "Detected failure", zh: "检测到失败" },
    body: {
      en: "Empty-grasp or timeout detection can trigger one deterministic retreat and retry, with every event logged.",
      zh: "空抓或超时检测可触发一次确定性撤回与重试，并完整记录事件。",
    },
    event: { en: "retry 1 / 1 · telemetry recorded", zh: "重试 1 / 1 · 遥测已记录" },
  },
];

export const features: Feature[] = [
  {
    eyebrow: "01 / VERSION",
    title: { en: "Invalidate stale intent", zh: "让过期意图失效" },
    body: {
      en: "Every command has a version. When it changes, queued policy actions from the previous version lose authority.",
      zh: "每条指令都有版本；版本变化后，旧版本排队动作不再具有执行权。",
    },
  },
  {
    eyebrow: "02 / SAFETY",
    title: { en: "Bound every action", zh: "约束每一步动作" },
    body: {
      en: "Joint bounds and rate limits are enforced before control reaches the Genesis Franka simulation.",
      zh: "在控制进入 Genesis Franka 仿真前，统一执行关节限幅与速率限制。",
    },
  },
  {
    eyebrow: "03 / RECOVERY",
    title: { en: "Retry once, visibly", zh: "一次可见、可审计的重试" },
    body: {
      en: "A bounded recovery policy retreats, reopens, and retries at most once instead of looping indefinitely.",
      zh: "有界恢复策略执行撤回、张爪，最多只重试一次，避免无限循环。",
    },
  },
];

const destinations: TaskRow["targets"] = [
  { label: { en: "white · left", zh: "白色 · 左侧" }, color: "white" },
  { label: { en: "blue · left", zh: "蓝色 · 左侧" }, color: "blue" },
  { label: { en: "white · right", zh: "白色 · 右侧" }, color: "white" },
  { label: { en: "blue · right", zh: "蓝色 · 右侧" }, color: "blue" },
];

export const taskRows: TaskRow[] = [
  { fruit: { en: "Banana", zh: "香蕉" }, targets: destinations },
  { fruit: { en: "Lemon", zh: "柠檬" }, targets: destinations },
  { fruit: { en: "Plum", zh: "李子" }, targets: destinations },
  { fruit: { en: "Apple", zh: "苹果" }, targets: destinations },
  { fruit: { en: "Orange", zh: "橙子" }, targets: destinations },
];

export function t(text: LocalizedText, locale: Locale): string {
  return text[locale];
}
