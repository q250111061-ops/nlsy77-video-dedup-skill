<div align="center">

# 🎬 nlsy77-video-dedup-skill

**面向 Claude Code / pi / Codex 的三层深度视频去重与过原创 AI Agent Skill**

*不靠糊画质的贴纸与畸变，从「物理音画指纹 · 大模型语义查重 · 非线性分镜结构」三层彻底解决搬运/二创/切片被判高度相似的问题*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-Claude_Code_%7C_pi_%7C_Codex-7c3aed)](./SKILL.md)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Hardware_Accelerated-007808?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![Whisper](https://img.shields.io/badge/ASR-Faster--Whisper-orange)](https://github.com/SYSTRAN/faster-whisper)

</div>

---

## 💡 为什么加了遮罩、改了 MD5 还是卡 500 播放？

现在主流视频平台（抖音 / 视频号 / 快手 / B站 / TikTok / YouTube Shorts）的查重早已升级为**多模态 AI 联合判定**。只改底层文件参数有两种死法：
1. **轻度改 MD5 / 抽帧**：过不了语音转文字后的**大模型语义查重**和**分镜序列比对**，直接提示“平台已有高度相似内容”。
2. **重度叠贴纸 / 鱼眼旋转 / 高斯模糊**：机器过了，但画面惨不忍睹，观众前 2 秒直接划走，完播率崩盘照样没流量。

**`nlsy77-video-dedup-skill`** 把剪辑高手的“真去重”拆解为可自动执行的**三层递进流水线**：

| 查重维度 | 传统低质洗片（易死号/低播放） | 本 Skill 解决方案（高原创度 + 保画质） |
| :--- | :--- | :--- |
| **1. 物理音画层** | 乱贴透明图、画面晃动、重度模糊 | **肉眼无感扰动**：元数据清零 + 静态安全区微裁切 + 随机色相/Gamma/动态颗粒 + **2.5% 极低不透明度程序化动态扫光** + 人声频段增强与粉红底噪填谱 |
| **2. 语义查重层** | 机械同义词替换（AI 一眼识破） | **抽骨架 + 增删改四步法**：Faster-Whisper 提取逐句文稿 → 剥离原句抽逻辑骨架 → 去 AI 味重写 → **增细节、删水词、改场景** |
| **3. 叙事结构层** | 按原视频时间轴从头顺剪（全网撞车） | **非线性高光前置 + 跨源混剪**：黄金前 3 秒高燃反转前置倒叙 + 多集/多场直播通用话术句级交叉拼接，生成全网唯一分镜序列 |

---

## 🚀 一键安装（支持主流 AI Coding Agent）

### Claude Code
```bash
git clone https://github.com/q250111061-ops/nlsy77-video-dedup-skill.git ~/.claude/skills/video-original-dedup
```

### pi / Codex / 通用 `~/.agents/skills`
```bash
git clone https://github.com/q250111061-ops/nlsy77-video-dedup-skill.git ~/.agents/skills/video-original-dedup
```

### 环境依赖
- **Python 3.9+**
- **FFmpeg**（macOS 默认开启 `h264_videotoolbox` 硬件加速；Linux/Windows 可传 `--encoder libx264`）
- **faster-whisper**（可选，仅在使用 `extract_script.py` 提取原视频语音文案时需要：`pip install faster-whisper`）

---

## 💬 在 Agent 中怎么用？（自然语言直接触发）

装好后无需记复杂参数，直接对 AI 说：

- **影视 / 日剧 / 公开课双语字幕搬运（保画质无感去重）**
  > “帮我把 `ep07_bilingual.mp4` 做无感音画去重，保持字幕不被裁切。”
- **带货 / 解说爆款文案洗稿二创（破 AI 语义查重）**
  > “提取 `hot_video.mp4` 的口播文案，按骨架增删改方法重写一份追剧场景的新口播稿，避开平台语义查重。”
- **AI 漫剧 / 直播切片混剪（破顺剪同质化）**
  > “分析这 5 集漫剧的台词时间戳，挑第 5 集最炸裂的反转做前 3 秒钩子，回接第 1 集世界观设定，拼接后做强化去重导出竖屏成片。”

---

## 🛠️ 命令行独立使用（不依赖 Agent 也能跑）

### 1. 音画物理去重（`scripts/dedup_av.py`）
```bash
# 无感模式（适合影视/双语字幕长视频，画质纯净）
python3 scripts/dedup_av.py input.mp4 output_dedup.mp4 --mode subtle

# 强化模式（含 2.5% 极低透明度动态微扫光 + 强化声纹微调，适合切片/带货/漫剧）
python3 scripts/dedup_av.py input.mp4 output_dedup.mp4 --mode aggressive
```

### 2. 提取逐句文案与时间戳（`scripts/extract_script.py`）
```bash
python3 scripts/extract_script.py input.mp4 script.json --lang zh
```

### 3. 非线性高光前置 / 跨源拼接（`scripts/reorder_concat.py`）
编写 `edl.json`（支持跨多个源文件抽取片段重组）：
```json
[
  {"file": "ep05.mp4", "start": 142.0, "end": 148.5, "note": "黄金前3秒高燃反转钩子"},
  {"file": "ep01.mp4", "start": 6.2, "end": 24.8, "note": "核心世界观设定回接"},
  {"file": "ep05.mp4", "start": 148.5, "end": 195.0, "note": "高潮正片延续"}
]
```
执行无缝重组并叠加去重：
```bash
python3 scripts/reorder_concat.py edl.json /tmp/reordered.mp4 --size 1080x1920
python3 scripts/dedup_av.py /tmp/reordered.mp4 final_original.mp4 --mode aggressive
```

---

## 📂 项目结构

```text
nlsy77-video-dedup-skill/
├── SKILL.md                    # Agent 核心工作流、红线规范与分层决策指南
├── README.md                   # 项目说明文档
├── LICENSE                     # MIT 开源协议
└── scripts/
    ├── dedup_av.py             # 第 1 层：FFmpeg 音画物理无感/强化去重引擎
    ├── extract_script.py       # 第 2/3 层：Faster-Whisper 句级文案与时间戳提取
    └── reorder_concat.py       # 第 3 层：EDL 非线性高光前置与跨源混剪合成器
```

---

## ⭐ Star History

如果这个 Skill 帮你的视频顺利过了原创、省下了剪辑洗片时间，欢迎点个 **Star ⭐** 支持！
