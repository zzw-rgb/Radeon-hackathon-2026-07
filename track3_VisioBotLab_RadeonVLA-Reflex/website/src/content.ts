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

export interface CollectionClip {
  index: string;
  episode: string;
  duration: string;
  frames: LocalizedText;
  video: string;
  poster: string;
  title: LocalizedText;
  instruction: LocalizedText;
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

export interface TeamMember {
  name: LocalizedText;
  role: LocalizedText;
  share: string;
  focus: LocalizedText;
  lead?: boolean;
}

export const projectLinks = {
  source:
    "https://github.com/zzw-rgb/Radeon-hackathon-2026-07/tree/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex",
  pages: "https://zzw-rgb.github.io/Radeon-hackathon-2026-07/",
  contest: "https://modelscope.cn/events/299/比赛介绍",
  baseModel: "https://huggingface.co/lerobot/smolvla_base",
  technicalReport:
    "https://github.com/zzw-rgb/Radeon-hackathon-2026-07/blob/submission/track3-visiobotlab-radeonvla-reflex/track3_VisioBotLab_RadeonVLA-Reflex/reports/RadeonVLA-Reflex-Technical-Report.md",
};

export const navItems: Array<{ href: string; label: LocalizedText }> = [
  { href: "#overview", label: { en: "Overview", zh: "概览" } },
  { href: "#demo", label: { en: "Evidence", zh: "核心演示" } },
  { href: "#runtime", label: { en: "Architecture", zh: "系统架构" } },
  { href: "#benchmark", label: { en: "Benchmark", zh: "基准" } },
  { href: "#team", label: { en: "Team", zh: "团队" } },
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
  demoCta: { en: "See the core demo plan", zh: "查看核心演示" },
  heroAlt: {
    en: "Collaborative robot holding an apple as a stale action path stops and a safe recovery path redirects toward the blue bowl",
    zh: "协作机械臂夹持苹果，失效动作路径停止，安全恢复路径转向蓝色碗",
  },
  placeholder: { en: "Original recovery concept art", zh: "原创恢复机制概念图" },
  proofLabel: { en: "Verified snapshot", zh: "已核验快照" },
  proofNote: {
    en: "Numbers below are from completed, audited artifacts only. Formal policy success on the Physical-1K checkpoint remains pending held-out evaluation.",
    zh: "下列数字仅来自已完成且可审计的产物；Physical-1K 最终 checkpoint 的策略成功率仍待独立评测。",
  },
  overviewKicker: { en: "WHAT WE BUILT", zh: "项目是什么" },
  overviewTitle: {
    en: "A safety layer around action-chunk VLA control.",
    zh: "为动作块 VLA 控制加上可审计的安全层。",
  },
  overviewBody: {
    en: "Fruit sorting is the Track 3 proving ground. The product idea is an interruptible, recoverable execution stack on one AMD Radeon GPU: Genesis dual-bowl simulation, LeRobot 0.6 recording, SmolVLA fine-tuning, and a Reflex monitor that can drop stale chunks when the operator changes the command.",
    zh: "水果分拣是 Track 3 的验证场景。产品形态是一张 AMD Radeon 上的可中断、可恢复执行栈：Genesis 双碗仿真、LeRobot 0.6 采集、SmolVLA 微调，以及操作员改指令时能丢弃过期动作块的 Reflex 监视器。",
  },
  overviewPoints: [
    {
      title: { en: "Language-addressable dual bowls", zh: "语言可区分的双碗布局" },
      body: {
        en: "Five YCB fruits × four fixed bowls (white/blue × left/right) yield twenty L1 tasks, plus L2–L4 spatial, sequential, and rule suites.",
        zh: "五种 YCB 水果 × 四个固定碗（白/蓝 × 左/右）构成 20 个 L1 任务，并扩展 L2–L4 空间、序列与规则套件。",
      },
    },
    {
      title: { en: "Strict physical demonstrations", zh: "严格物理的专家演示" },
      body: {
        en: "Training data forbids kinematic grasp glue and placement teleports. Each episode carries a certificate with zero intervention counts.",
        zh: "训练数据禁止运动学粘附抓取与放置瞬移；每条 episode 附带干预计数为 0 的严格物理证书。",
      },
    },
    {
      title: { en: "Single-GPU ROCm path", zh: "单卡 ROCm 全链路" },
      body: {
        en: "Record, train, evaluate, and benchmark on one visible Radeon device with immutable JSON/CSV/Markdown evidence.",
        zh: "在单张可见 Radeon 上完成采集、训练、评测与压力测试，并输出不可变 JSON/CSV/Markdown 证据。",
      },
    },
  ],
  sectionDemoKicker: { en: "JUDGE-FACING STORY", zh: "核心演示故事线" },
  sectionDemoTitle: {
    en: "Three moments. One execution layer.",
    zh: "三个关键时刻，一套执行层。",
  },
  sectionDemoBody: {
    en: "The final narrated walkthrough will show the same checkpoint under normal execution, a mid-command change, and recovery after a detected failure. That policy video is the core evidence—not the data-collection smoke clips below.",
    zh: "最终解说视频将使用同一 checkpoint，展示正常执行、中途改指令，以及检测到失败后的恢复。那才是核心演示证据——下方的数据采集冒烟片段只是辅助。",
  },
  videoLabel: { en: "3+ MIN POLICY WALKTHROUGH", zh: "3 分钟以上策略解说视频" },
  videoPending: { en: "Pending final evaluation recordings", zh: "等待最终评测录制" },
  videoBody: {
    en: "Interrupt / recover / success narrative with captions. Collection smoke clips are filed separately under Data pipeline and are not a substitute for this slot.",
    zh: "中断 / 恢复 / 成功叙事，并配字幕。采集冒烟片段放在「数据链路」辅助区，不占用本核心位。",
  },
  // Secondary appendix: local data-collection smoke only (not policy demo)
  collectionKicker: { en: "DATA PIPELINE APPENDIX", zh: "数据链路附录" },
  collectionTitle: {
    en: "Local collection smoke clips (not the final demo).",
    zh: "本机采集冒烟片段（非最终演示）。",
  },
  collectionBody: {
    en: "Optional H.264 excerpts from the local 200-episode expert baseline. They only prove the recording path; they are not the Track 3 policy demonstration video.",
    zh: "可选的本机 200 条专家基线 H.264 摘录，仅证明采集链路可跑通，不是赛道最终策略演示视频。",
  },
  videoCollectionLabel: { en: "COLLECTION SMOKE ONLY", zh: "仅采集冒烟" },
  videoCollectionPending: { en: "Expert recording preview · not policy eval", zh: "专家采集预览 · 非策略评测" },
  videoCollectionBody: {
    en: "Apple→blue-left, banana→white-right, plum→white-left. Compact previews—open only if you want data-path detail.",
    zh: "苹果→左蓝、香蕉→右白、李子→左白。紧凑预览，仅在需要核对数据链路时展开。",
  },
  clipState: { en: "COLLECTION CLIP", zh: "采集片段" },
  clipCamera: { en: "WORLD RGB · 20 FPS", zh: "世界相机 RGB · 20 FPS" },
  clipPlayLabel: { en: "Play collection smoke clip", zh: "播放采集冒烟片段" },
  clipFallback: {
    en: "Your browser cannot play this H.264 video.",
    zh: "当前浏览器无法播放此 H.264 视频。",
  },
  collectionScopeTitle: { en: "Scope", zh: "范围" },
  collectionScopeBody: {
    en: "Scripted expert data only. Does not replace the pending interrupt/recovery policy video in the core evidence section.",
    zh: "仅脚本专家数据。不能替代核心证据区待补的中断/恢复策略视频。",
  },
  collectionStats: [
    { value: "200", label: { en: "local successes", zh: "本机成功条数" } },
    { value: "20×10", label: { en: "L1 coverage", zh: "L1 任务覆盖" } },
    { value: "46k", label: { en: "frames", zh: "帧数" } },
    { value: "aux", label: { en: "not core demo", zh: "非核心演示" } },
  ],
  plannedEvidence: { en: "Core policy moments", zh: "核心策略时刻" },
  runtimeKicker: { en: "SYSTEM ARCHITECTURE", zh: "系统架构" },
  runtimeTitle: { en: "The policy proposes. The runtime decides.", zh: "策略提出动作，运行层决定是否执行。" },
  runtimeBody: {
    en: "Action chunking improves throughput, but an old chunk can outlive the instruction that created it. Reflex is the deterministic boundary between learned control and Genesis.",
    zh: "动作分块可以提升吞吐，但旧动作块可能比生成它的指令活得更久。Reflex 是学习控制与 Genesis 之间的确定性边界。",
  },
  architectureDiagramAlt: {
    en: "System architecture diagram: world and wrist RGB plus robot state feed SmolVLA; action chunks pass through the execution safety monitor into Genesis Franka dual-bowl simulation",
    zh: "系统架构图：世界/腕部 RGB 与机器人状态输入 SmolVLA；动作块经执行安全监视器进入 Genesis Franka 双碗仿真",
  },
  architectureDiagramCaption: {
    en: "Closed loop — perception → SmolVLA → Reflex safety monitor → Genesis dual-bowl sim → next observation.",
    zh: "闭环：感知 → SmolVLA → Reflex 安全监视器 → Genesis 双碗仿真 → 下一帧观测。",
  },
  architectureLabel: { en: "Compact execution path", zh: "精简执行路径" },
  architectureInput: { en: "Language + RGB + state", zh: "语言 + RGB + 状态" },
  architecturePolicy: { en: "SmolVLA policy", zh: "SmolVLA 策略" },
  architectureReflex: { en: "Reflex runtime", zh: "Reflex 运行层" },
  architectureSafety: { en: "invalidate · clamp · retry", zh: "失效 · 限幅 · 重试" },
  architectureSim: { en: "Genesis + Franka", zh: "Genesis + Franka" },
  benchmarkKicker: { en: "PRIMARY BENCHMARK", zh: "主要基准" },
  benchmarkTitle: { en: "Five fruits. Four destinations. Twenty tasks.", zh: "五种水果，四个盘位，二十项任务。" },
  benchmarkBody: {
    en: "L1 crosses every fruit with every language-addressable bowl. Baseline demos: 10 per task (200 total). Formal Physical-1K target: 50 per task (1,000 total) under strict physics.",
    zh: "L1 将每种水果与每个语言可指定盘位交叉。基线演示：每任务 10 条（共 200）。正式 Physical-1K 目标：严格物理下每任务 50 条（共 1,000）。",
  },
  targetLabel: { en: "Destination", zh: "目标盘位" },
  objectLabel: { en: "Object", zh: "物体" },
  demosLabel: { en: "10 baseline · 50 formal", zh: "基线 10 · 正式 50" },
  evidenceKicker: { en: "NO PLACEHOLDER CLAIMS", zh: "不使用占位成绩" },
  evidenceTitle: { en: "Measured results, or a clear Pending.", zh: "只展示实测结果，否则明确标记待完成。" },
  evidenceBody: {
    en: "The baseline dataset proves the recording path. Physical-1K collection, SmolVLA fine-tuning, latency, and Reflex ablations publish only from immutable evaluation artifacts.",
    zh: "基线数据集证明采集链路可用。Physical-1K 采集、SmolVLA 微调、延迟与 Reflex 消融仅从不可变评测产物发布。",
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
  releaseTarget: { en: "Formal training target", zh: "正式训练目标" },
  releaseTargetValue: { en: "1,000 demos · 20 × 50", zh: "1,000 条演示 · 20 × 50" },
  releaseTargetBody: {
    en: "Balanced strict-physics expert set with a disjoint validation seed range. Cloud collection runs in fruit shards then merges under certificate checks.",
    zh: "均衡的严格物理专家集，验证 seed 与训练不相交。云端按水果分片采集，再经证书校验合并。",
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
    en: "Nanjing University of Science and Technology · Track 3 Physical AI Challenge",
    zh: "南京理工大学 · Track 3 Physical AI 挑战赛",
  },
  teamLeadLabel: { en: "Team captain", zh: "队长" },
  teamMemberLabel: { en: "Member", zh: "队员" },
  teamShareLabel: { en: "Effort share", zh: "工作量占比" },
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
    label: { en: "local smoke demos", zh: "本机冒烟演示" },
    detail: { en: "manifest complete · 20 × 10", zh: "manifest 完成 · 20 × 10" },
  },
  {
    value: "1,000",
    label: { en: "Physical-1K cloud demos", zh: "云端 Physical-1K" },
    detail: { en: "strict physics · 20 × 50", zh: "严格物理 · 20 × 50" },
  },
  {
    value: "46,420",
    label: { en: "local baseline frames", zh: "本机基线帧数" },
    detail: { en: "20 Hz dual RGB smoke set", zh: "20 Hz 双路 RGB 冒烟集" },
  },
  {
    value: "1× GPU",
    label: { en: "AMD Radeon path", zh: "AMD Radeon 路径" },
    detail: { en: "ROCm sim · train · eval", zh: "ROCm 仿真 · 训练 · 评测" },
  },
];

export const teamMembers: TeamMember[] = [
  {
    name: { en: "Zhenwei Zhou", zh: "周振威" },
    role: { en: "Team captain · lead engineer", zh: "队长 · 主程" },
    share: "70%",
    lead: true,
    focus: {
      en: "System architecture, Genesis scene & expert, strict-physics collection, SmolVLA train/eval, website, and submission.",
      zh: "系统架构、Genesis 场景与专家策略、严格物理采集、SmolVLA 训练评测、网站与最终提交。",
    },
  },
  {
    name: { en: "Ange Liu", zh: "留安格" },
    role: { en: "Member · docs & presentation", zh: "队员 · 文档与展示" },
    share: "15%",
    focus: {
      en: "Bilingual documentation polish, task-suite wording review, and showcase copy support.",
      zh: "中英文文档润色、任务表述校对，以及展示文案协助。",
    },
  },
  {
    name: { en: "Haoran Wang", zh: "王浩然" },
    role: { en: "Member · QA & reporting", zh: "队员 · 质检与报告" },
    share: "15%",
    focus: {
      en: "Dataset spot-checks, experiment logging, and technical-report / evidence packaging support.",
      zh: "数据抽检、实验记录整理，以及技术报告与证据打包协助。",
    },
  },
];

export const collectionClips: CollectionClip[] = [
  {
    index: "01",
    episode: "000",
    duration: "10.45 s",
    frames: { en: "209 frames", zh: "209 帧" },
    video: "videos/dataset-apple-blue-left.mp4",
    poster: "videos/dataset-apple-blue-left.webp",
    title: { en: "Apple → blue bowl, left", zh: "苹果 → 左侧蓝碗" },
    instruction: {
      en: "Pick the apple and place it in the blue bowl on the left.",
      zh: "抓取苹果并放入左侧蓝碗。",
    },
  },
  {
    index: "02",
    episode: "047",
    duration: "12.55 s",
    frames: { en: "251 frames", zh: "251 帧" },
    video: "videos/dataset-banana-white-right.mp4",
    poster: "videos/dataset-banana-white-right.webp",
    title: { en: "Banana → white bowl, right", zh: "香蕉 → 右侧白碗" },
    instruction: {
      en: "Pick the banana and place it in the white bowl on the right.",
      zh: "抓取香蕉并放入右侧白碗。",
    },
  },
  {
    index: "03",
    episode: "158",
    duration: "12.10 s",
    frames: { en: "242 frames", zh: "242 帧" },
    video: "videos/dataset-plum-white-left.mp4",
    poster: "videos/dataset-plum-white-left.webp",
    title: { en: "Plum → white bowl, left", zh: "李子 → 左侧白碗" },
    instruction: {
      en: "Pick the plum and place it in the white bowl on the left.",
      zh: "抓取李子并放入左侧白碗。",
    },
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
