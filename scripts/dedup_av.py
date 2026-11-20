#!/usr/bin/env python3
"""
视频音画物理去重脚本（对应去重方法论第一层：画面 + 音频 + 元数据）
支持 subtle（无感模式，适合影视/双语剧集）与 aggressive（强化模式，含微扫光叠加，适合切片/带货）。
"""

from __future__ import annotations

import argparse
import os
import random
import subprocess
import sys


def get_video_info(input_path: str) -> tuple[int, int, float]:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "csv=p=0",
        input_path,
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    parts = out.split(",")
    w, h = int(parts[0]), int(parts[1])
    num, den = parts[2].split("/")
    fps = float(num) / float(den) if float(den) != 0 else 30.0
    return w, h, fps


def build_filter_complex(w: int, h: int, mode: str, seed: int | None = None) -> tuple[str, str]:
    rng = random.Random(seed)

    # 1. 微裁切放大（保持静止，不晃动，不裁掉字幕安全区）
    crop_ratio = 0.982 if mode == "subtle" else 0.965
    cw = int(w * crop_ratio) // 2 * 2
    ch = int(h * crop_ratio) // 2 * 2
    max_x = max(0, w - cw)
    max_y = max(0, h - ch)
    cx = rng.randint(0, max_x) // 2 * 2 if max_x > 0 else 0
    cy = rng.randint(0, max_y) // 2 * 2 if max_y > 0 else 0

    # 2. 色彩/色相/锐化/动态颗粒随机微调（保证肉眼观感自然不糊）
    contrast = round(rng.uniform(1.02, 1.045), 3)
    saturation = round(rng.uniform(1.03, 1.07), 3)
    brightness = round(rng.uniform(0.004, 0.012), 3)
    gamma = round(rng.uniform(1.008, 1.022), 3)
    hue_shift = rng.choice([-3, -2, 2, 3])
    noise_level = 3 if mode == "subtle" else 5

    # 3. 音频去重参数前置计算，确保视频 setpts 与音频 pitch_factor * tempo 严格同速不音画错位
    pitch_factor = round(rng.uniform(1.018, 1.035), 4) if mode == "subtle" else round(rng.uniform(1.03, 1.055), 4)
    tempo = round(rng.uniform(1.008, 1.015), 3) if mode == "subtle" else round(rng.uniform(1.02, 1.05), 3)
    total_speed = round(pitch_factor * tempo, 6)
    noise_amp = 0.010 if mode == "subtle" else 0.015

    v_chain = (
        f"[0:v]setpts=PTS/{total_speed},fps=30,crop={cw}:{ch}:{cx}:{cy},scale={w}:{h}:flags=lanczos,"
        f"eq=contrast={contrast}:saturation={saturation}:brightness={brightness}:gamma={gamma},"
        f"hue=h={hue_shift},unsharp=3:3:0.25,noise=alls={noise_level}:allf=t+u"
    )

    if mode == "aggressive":
        # 对应视频中“极低透明度扫光/动态干扰层”：用程序化动态微亮光带以 2.5% 不透明度叠加
        v_filter = (
            f"{v_chain},format=rgba[base];"
            f"color=c=black@0.0:s={w}x{h}:r=30,format=rgba,"
            f"geq=r='255':g='255':b='255':a='if(lt(abs((X+Y*0.4)-mod(T*380,{w}+{h})),90),7,0)'[sweep];"
            f"[base][sweep]overlay=0:0:shortest=1,format=yuv420p[vout]"
        )
    else:
        v_filter = f"{v_chain},format=yuv420p[vout]"

    a_filter = (
        f"[0:a]asetrate=48000*{pitch_factor},aresample=48000,atempo={tempo},"
        f"equalizer=f=150:width_type=o:width=1.2:g=-1.5,"
        f"equalizer=f=2400:width_type=o:width=1.4:g=1.8,"
        f"equalizer=f=3200:width_type=o:width=1.5:g=1.2[voice];"
        f"anoisesrc=color=pink:r=48000:a={noise_amp}[pink];"
        f"[voice][pink]amix=inputs=2:duration=first:weights=1 0.28[aout]"
    )

    return v_filter, a_filter


def main() -> None:
    parser = argparse.ArgumentParser(description="音画物理去重处理器")
    parser.add_argument("input", help="输入视频路径")
    parser.add_argument("output", help="输出视频路径")
    parser.add_argument("--mode", choices=["subtle", "aggressive"], default="subtle",
                        help="subtle=无感模式(适合影视/双语字幕), aggressive=强化模式(含微扫光叠加,适合切片/带货)")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（可选，用于复现参数）")
    parser.add_argument("--encoder", default="h264_videotoolbox", help="视频编码器，默认 h264_videotoolbox，可选 libx264")
    parser.add_argument("--bitrate", default="5200k", help="视频码率，默认 5200k")
    parser.add_argument("--dry-run", action="store_true", help="仅打印 ffmpeg 命令不执行")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    w, h, _ = get_video_info(args.input)
    v_filter, a_filter = build_filter_complex(w, h, args.mode, args.seed)
    filter_complex = f"{v_filter};{a_filter}"

    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-map_metadata", "-1",
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", args.encoder,
    ]
    if args.encoder == "h264_videotoolbox":
        cmd += ["-profile:v", "high", "-b:v", args.bitrate]
    else:
        cmd += ["-preset", "medium", "-crf", "20"]

    cmd += [
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        args.output,
    ]

    print("FFmpeg command:")
    print(" ".join(cmd))
    if args.dry_run:
        return

    subprocess.run(cmd, check=True)
    print(f"Done: {args.output}")


if __name__ == "__main__":
    main()
