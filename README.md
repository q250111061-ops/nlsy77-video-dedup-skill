# video-original-dedup

面向 AI Agent（Claude Code / pi / Codex 等）的**三层深度视频去重与过原创 Skill**。

不依赖破坏观感的重度模糊或杂乱贴纸，从**物理音画特征**、**大模型语义查重**、**分镜叙事结构**三个维度解决短视频/影视搬运与切片二创被判“高度相似”的问题。

## 核心三层方法论

1. **第 1 层：物理音画无感去重（`scripts/dedup_av.py`）**
   - 清空容器与流元数据（`-map_metadata -1`）
   - 安全区静态微裁切放大（不晃动、不裁字幕）+ 随机微调对比度/饱和度/Gamma/色相 + 时间随机动态颗粒
   - `aggressive` 模式额外叠加 **~2.5% 极低不透明度程序化动态微扫光层**（肉眼无感，彻底打散帧哈希）
   - 人声核心频段增强 + 轻微音高/语速偏移 + 极低电平粉红底噪填平频谱
2. **第 2 层：文案语义去重——「抽骨架 + 增删改」四步法**
   - 用 `scripts/extract_script.py`（基于 `faster-whisper`）提取逐句口播文案与时间戳
   - 严禁机械同义词替换，按“抽离逻辑骨架 → 去 AI 味口语化重写 → 增细节 / 删水词 / 改场景”重构文案，绕过平台 AI 语义查重
3. **第 3 层：非线性结构重组 & 跨源混剪（`scripts/reorder_concat.py`）**
   - 针对不能改原声的直播切片、AI 漫剧、影视混剪：支持**黄金前 3 秒高光前置倒叙**与**跨场次/跨集句级交叉拼接**，打破全网顺剪同质化

## 环境依赖

- Python 3.9+
- FFmpeg（macOS 默认使用 `h264_videotoolbox` 硬件加速，其他平台可传 `--encoder libx264`）
- `faster-whisper`（仅运行 `extract_script.py` 提取语音文案时需要）

## 安装为 Agent Skill

```bash
git clone https://github.com/q250111061-ops/nlsy77-video-dedup.git ~/.agents/skills/video-original-dedup
```

## 命令行单独调用示例

```bash
# 1. 无感模式音画去重（适合影视/双语字幕长视频）
python3 scripts/dedup_av.py input.mp4 output_dedup.mp4 --mode subtle

# 2. 强化模式音画去重（含极低透明度动态微扫光，适合切片/带货/漫剧）
python3 scripts/dedup_av.py input.mp4 output_dedup.mp4 --mode aggressive

# 3. 提取视频逐句文案与时间戳
python3 scripts/extract_script.py input.mp4 script.json --lang zh

# 4. 按 EDL JSON 非线性高光前置 / 跨源拼接
python3 scripts/reorder_concat.py edl.json reordered.mp4 --size 1080x1920
```

详细 Agent 工作流规范见 [`SKILL.md`](./SKILL.md)。
