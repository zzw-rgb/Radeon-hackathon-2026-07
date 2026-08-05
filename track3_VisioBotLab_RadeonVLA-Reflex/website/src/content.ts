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
  dataset: "https://huggingface.co/datasets/a3124371940/radeonvla_reflex_physical_2k",
  model50k: "https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_1k_50k",
  finalModel: "https://huggingface.co/a3124371940/radeonvla_reflex_smolvla_2k_200k",
  evaluationVideos: "https://huggingface.co/datasets/a3124371940/radeonvla_reflex_evaluation_videos",
};

export const navItems: Array<{ href: string; label: LocalizedText }> = [
  { href: "#overview", label: { en: "Overview", zh: "概览" } },
  { href: "#demo", label: { en: "Evidence", zh: "核心演示" } },
  { href: "#runtime", label: { en: "Architecture", zh: "系统架构" } },
  { href: "#benchmark", label: { en: "Benchmark", zh: "基准" } },
  { href: "./console.html", label: { en: "Console", zh: "控制台" } },
  { href: "#reproduce", label: { en: "Reproduce", zh: "复现" } },
  { href: "#team", label: { en: "Team", zh: "团队" } },
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
    en: "RadeonVLA-Reflex wraps a vision-language-action policy with command invalidation, safe interruption, and bounded strict-physics recovery—so stale or failed action chunks do not stay in control.",
    zh: "RadeonVLA-Reflex 在视觉语言动作策略外加入指令失效、安全中断与有界严格物理恢复，避免过期或失败的动作块继续控制机械臂。",
  },
  sourceCta: { en: "Explore the source", zh: "查看项目源码" },
  demoCta: { en: "See the core demonstration", zh: "查看核心演示" },
  consoleCta: { en: "Launch evidence console", zh: "进入可视化控制台" },
  heroAlt: {
    en: "Collaborative robot holding an apple as a stale action path stops and a safe recovery path redirects toward the blue bowl",
    zh: "协作机械臂夹持苹果，失效动作路径停止，安全恢复路径转向蓝色碗",
  },
  placeholder: { en: "Original recovery concept art", zh: "原创恢复机制概念图" },
  proofLabel: { en: "Verified snapshot", zh: "已核验快照" },
  proofNote: {
    en: "This snapshot separates completed local artifacts from formal release targets. Policy metrics are published from held-out evaluation artifacts.",
    zh: "该快照区分已完成的本地产物与正式发布目标；策略指标以独立评测产物为准。",
  },
  overviewKicker: { en: "SYSTEM OVERVIEW", zh: "系统概览" },
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
  sectionDemoKicker: { en: "CORE DEMONSTRATION", zh: "核心演示" },
  sectionDemoTitle: {
    en: "Three moments. One execution layer.",
    zh: "三个关键时刻，一套执行层。",
  },
  sectionDemoBody: {
    en: "The core walkthrough uses one checkpoint for normal execution, an apple mid-command change, and recovery after a detected failure. Representative learned-policy successes are published separately with fixed seeds and hashes.",
    zh: "核心演示使用同一 checkpoint 展示正常执行、苹果中途改令，以及检测到失败后的恢复；学习策略成功代表片段按固定 seed 与哈希独立发布。",
  },
  videoLabel: { en: "3+ MIN POLICY WALKTHROUGH", zh: "3 分钟以上策略解说视频" },
  videoPending: { en: "Narrated project walkthrough · 3+ min", zh: "项目解说成片 · 3 分钟以上" },
  videoBody: {
    en: "A smooth 200-second English walkthrough of Physical-2K, the Radeon training path, the 200K checkpoint, representative non-banana successes, a real learned miss, and strict-physics recovery. English and Chinese captions remain inside a dedicated safe-area bar.",
    zh: "200 秒自然英文旁白完整讲解 Physical-2K、Radeon 训练、200K 权重、非香蕉成功案例、真实空抓和严格物理恢复；中英双语字幕固定在独立安全底栏。",
  },
  comparisonLabel: { en: "15 SEC PAIRED EVIDENCE", zh: "15 秒同条件对照" },
  comparisonTitle: {
    en: "Learned miss → strict-physics recovery",
    zh: "学习策略空抓 → 严格物理恢复",
  },
  comparisonBody: {
    en: "Two fixed-seed apple rollouts from the 200K checkpoint: the learned attempt on the left and the explicitly labeled Precision Reflex path on the right. No object teleport or grasp glue is permitted.",
    zh: "两条使用 200K 权重和相同固定 seed 的苹果闭环：左侧为学习策略尝试，右侧为显式标记的 Precision Reflex 路径；全程禁止物体瞬移和抓取粘附。",
  },
  interruptLabel: { en: "47.8 SEC INTERRUPT + RECOVERY", zh: "47.8 秒改令与恢复证据" },
  interruptTitle: {
    en: "Apple white-left invalidated → blue-right recovered",
    zh: "苹果左白指令作废 → 恢复后完成右蓝任务",
  },
  interruptBody: {
    en: "At step 40, seed 61000 changes apple→white-left to apple→blue-right. The stale chunk stops with 0 extra response steps and 0 unprotected actions. The learned continuation then empty-grasps, so the explicitly labeled strict-physics recovery finishes the new task: final success 1/1.",
    zh: "固定 seed 61000 在第 40 步把苹果→左白改为苹果→右蓝；旧动作块以额外响应 0 步、未保护动作 0 步立即停止。学习控制随后空抓，因此由明确标注的严格物理恢复完成新任务，最终成功 1/1。",
  },
  // Supporting appendix for released representative evaluation replays.
  collectionKicker: { en: "EVALUATION REPLAY LIBRARY", zh: "评测回放库" },
  collectionTitle: {
    en: "Representative learned-policy successes.",
    zh: "学习策略首次成功代表片段。",
  },
  collectionBody: {
    en: "Four H.264 rollouts from the released 200K checkpoint show first-attempt successes for apple, lemon, orange, and plum. The full evidence bundle is published independently on Hugging Face.",
    zh: "四段来自已发布 200K 权重的 H.264 闭环，展示苹果、柠檬、橙子和李子的学习策略首次成功；完整证据包已独立发布到 Hugging Face。",
  },
  videoCollectionLabel: { en: "200K POLICY REPLAYS", zh: "200K 策略回放" },
  videoCollectionPending: { en: "Successful non-banana evaluation rollouts", zh: "非香蕉评测成功片段" },
  videoCollectionBody: {
    en: "Each clip is linked to a task, fixed seed, 200K checkpoint hash, and machine-readable result.",
    zh: "每段视频均关联具体任务、固定 seed、200K 权重哈希和机器可读评测结果。",
  },
  clipState: { en: "FIRST-TRY SUCCESS", zh: "首次执行成功" },
  clipCamera: { en: "WORLD RGB · 20 FPS", zh: "世界相机 RGB · 20 FPS" },
  clipPlayLabel: { en: "Play evaluation replay", zh: "播放评测回放" },
  clipFallback: {
    en: "H.264 playback is unavailable in this browser.",
    zh: "当前浏览器无法播放此 H.264 视频。",
  },
  collectionScopeTitle: { en: "Scope", zh: "范围" },
  collectionScopeBody: {
    en: "These are representative policy replays, not the denominator itself. Aggregate claims remain tied to the released 100-rollout JSON/CSV evidence.",
    zh: "这些是代表性策略回放，并非评测分母本身；汇总指标仍以已发布的 100 次 JSON/CSV 证据为准。",
  },
  collectionStats: [
    { value: "4", label: { en: "released replays", zh: "公开回放" } },
    { value: "4", label: { en: "fruit classes", zh: "水果类别" } },
    { value: "200K", label: { en: "checkpoint", zh: "模型权重" } },
    { value: "100", label: { en: "formal denominator", zh: "正式评测分母" } },
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
    en: "L1 crosses every fruit with every language-addressable bowl. Physical-2K contains 100 strict-physics demonstrations per task—2,000 episodes and 468,889 dual-camera frames in total.",
    zh: "L1 将每种水果与每个语言可指定盘位交叉。Physical-2K 每项任务包含 100 条严格物理演示，共 2,000 个 episode、468,889 帧双相机数据。",
  },
  targetLabel: { en: "Destination", zh: "目标盘位" },
  objectLabel: { en: "Object", zh: "物体" },
  demosLabel: { en: "100 strict demos", zh: "100 条严格演示" },
  evidenceKicker: { en: "EVALUATION STATUS", zh: "评测状态" },
  evidenceTitle: { en: "Evidence organized by completion state.", zh: "按完成状态组织评测证据。" },
  evidenceBody: {
    en: "Physical-2K, the 200K checkpoint, latency, first-attempt success, and Reflex final success are reported from immutable evaluation artifacts with disjoint seeds.",
    zh: "Physical-2K、200K checkpoint、推理延迟、首次成功率和 Reflex 最终成功率均来自独立 seed 的不可变评测产物。",
  },
  releaseTarget: { en: "Released training dataset", zh: "已发布训练数据集" },
  releaseTargetValue: { en: "2,000 demos · 20 × 100", zh: "2,000 条演示 · 20 × 100" },
  releaseTargetBody: {
    en: "Balanced strict-physics expert set with 2,000 episode certificates, zero kinematic interventions, complete task coverage, and a fixed Hugging Face revision.",
    zh: "均衡严格物理专家集，包含 2,000 份 episode 证书、零运动学干预、完整任务覆盖和固定 Hugging Face revision。",
  },
  datasetCta: { en: "Open Physical-2K dataset", zh: "查看 Physical-2K 数据集" },
  modelLabel: { en: "Base policy", zh: "基础策略" },
  modelValue: { en: "LeRobot / SmolVLA", zh: "LeRobot / SmolVLA" },
  modelBody: {
    en: "Fine-tuned for 9-D absolute joint-position control from two RGB views and language.",
    zh: "使用双路 RGB 与语言输入，微调为 9 维绝对关节位置控制。",
  },
  baseModelCta: { en: "Open base model", zh: "查看基础模型" },
  trainedModelCta: { en: "Open final 200K checkpoint", zh: "查看最终 200K 权重" },
  evaluationVideosLabel: { en: "Evaluation evidence", zh: "评测证据" },
  evaluationVideosValue: { en: "Videos + JSON + checksums", zh: "视频 + JSON + 校验和" },
  evaluationVideosBody: {
    en: "A separate public Hugging Face dataset keeps representative replays, the 100-rollout bundle, interrupt evidence, and content hashes together.",
    zh: "独立公开的 Hugging Face 数据集统一保存代表性回放、100 次评测包、中断证据与内容哈希。",
  },
  evaluationVideosCta: { en: "Open evaluation videos", zh: "查看评测视频仓库" },
  reproduceKicker: { en: "REPRODUCIBLE PIPELINE", zh: "可复现链路" },
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
    en: "Scope is limited to Genesis simulation, the registered fruit-and-bowl tasks, two RGB views, and 9-D joint-position control. Real-robot transfer is outside the current evaluation.",
    zh: "当前范围限于 Genesis 仿真、已注册的水果与碗任务、双路 RGB 和 9 维关节位置控制；真实机械臂迁移不在本轮评测范围内。",
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
    en: "Project-owned RadeonVLA-Reflex hero concept. Third-party software and simulation credits are listed in THIRD_PARTY_NOTICES.md.",
    zh: "RadeonVLA-Reflex 项目自有封面概念图；第三方软件与仿真署名详见 THIRD_PARTY_NOTICES.md。",
  },
} satisfies Record<string, unknown>;

export const verifiedMetrics: Metric[] = [
  {
    value: "2,000",
    label: { en: "strict-physics demos", zh: "严格物理演示" },
    detail: { en: "Physical-2K · 20 × 100", zh: "Physical-2K · 20 × 100" },
  },
  {
    value: "468,889",
    label: { en: "dual-camera frames", zh: "双相机数据帧" },
    detail: { en: "20 Hz · validator clean", zh: "20 Hz · 严格验证通过" },
  },
  {
    value: "200K",
    label: { en: "cumulative train steps", zh: "累计训练步数" },
    detail: { en: "SmolVLA · Physical-2K", zh: "SmolVLA · Physical-2K" },
  },
  {
    value: "1× GPU",
    label: { en: "AMD Radeon path", zh: "AMD Radeon 路径" },
    detail: { en: "ROCm sim · train · eval", zh: "ROCm 仿真 · 训练 · 评测" },
  },
];

export const evaluationMetrics: Metric[] = [
  {
    value: "91 / 100",
    label: { en: "final system success", zh: "最终系统成功" },
    detail: { en: "Wilson 95% CI · 83.8–95.2%", zh: "Wilson 95% 区间 · 83.8–95.2%" },
  },
  {
    value: "36 / 100",
    label: { en: "learned first attempt", zh: "学习策略首次成功" },
    detail: { en: "reported separately from recovery", zh: "与恢复贡献分开报告" },
  },
  {
    value: "+55",
    label: { en: "precision recoveries", zh: "精确恢复贡献" },
    detail: { en: "55 / 63 attempts · strict physics", zh: "55 / 63 次 · 严格物理" },
  },
  {
    value: "37.27 ms",
    label: { en: "P95 inference latency", zh: "P95 推理延迟" },
    detail: { en: "P50 4.54 ms · shared-GPU run", zh: "P50 4.54 ms · 共享 GPU 评测" },
  },
];

export const teamMembers: TeamMember[] = [
  {
    name: { en: "Zhenwei Zhou", zh: "周振威" },
    role: { en: "Team captain · lead engineer", zh: "队长 · 主程" },
    share: "70%",
    lead: true,
    focus: {
      en: "System architecture, Genesis scene and expert, strict-physics collection, SmolVLA training and evaluation, website, and release engineering.",
      zh: "系统架构、Genesis 场景与专家策略、严格物理采集、SmolVLA 训练评测、网站与发布工程。",
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
    episode: "50020",
    duration: "49.50 s",
    frames: { en: "fixed seed 50020", zh: "固定 seed 50020" },
    video: "videos/eval-apple-blue-left.mp4",
    poster: "videos/eval-apple-blue-left.webp",
    title: { en: "Apple → blue bowl, left", zh: "苹果 → 左侧蓝碗" },
    instruction: {
      en: "Pick the apple and place it in the blue bowl on the left.",
      zh: "抓取苹果并放入左侧蓝碗。",
    },
  },
  {
    index: "02",
    episode: "50022",
    duration: "7.80 s",
    frames: { en: "fixed seed 50022", zh: "固定 seed 50022" },
    video: "videos/eval-lemon-blue-right.mp4",
    poster: "videos/eval-lemon-blue-right.webp",
    title: { en: "Lemon → blue bowl, right", zh: "柠檬 → 右侧蓝碗" },
    instruction: {
      en: "Pick the lemon and place it in the blue bowl on the right.",
      zh: "抓取柠檬并放入右侧蓝碗。",
    },
  },
  {
    index: "03",
    episode: "50023",
    duration: "26.20 s",
    frames: { en: "fixed seed 50023", zh: "固定 seed 50023" },
    video: "videos/eval-orange-white-right.mp4",
    poster: "videos/eval-orange-white-right.webp",
    title: { en: "Orange → white bowl, right", zh: "橙子 → 右侧白碗" },
    instruction: {
      en: "Pick the orange and place it in the white bowl on the right.",
      zh: "抓取橙子并放入右侧白碗。",
    },
  },
  {
    index: "04",
    episode: "50024",
    duration: "24.50 s",
    frames: { en: "fixed seed 50024", zh: "固定 seed 50024" },
    video: "videos/eval-plum-white-left.mp4",
    poster: "videos/eval-plum-white-left.webp",
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
    state: "PRECISION",
    title: { en: "Strict-physics precision recovery", zh: "严格物理精确恢复" },
    body: {
      en: "After the learned retry budget is exhausted, a bounded geometry-aware recovery can finish the task while rigid pose writes remain forbidden.",
      zh: "学习策略用尽重试预算后，有界几何恢复可在继续禁止刚体位姿写入的前提下完成任务。",
    },
    event: { en: "strict physics · no teleport · logged", zh: "严格物理 · 无瞬移 · 全程留证" },
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
    title: { en: "Recover visibly and honestly", zh: "可见且诚实地恢复" },
    body: {
      en: "Evidence separates the learned first attempt from strict-physics recovery contribution instead of folding both into one opaque score.",
      zh: "评测把学习策略首抓与严格物理恢复贡献分开报告，不把两者折叠成一个不透明分数。",
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
