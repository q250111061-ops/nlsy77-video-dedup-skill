#!/usr/bin/env python3
"""
非线性结构重组与跨源混剪脚本（对应去重方法论第三层：高光前置 + 跨源片段拼接）
读取 JSON 格式的 EDL 片段列表，统一分辨率与采样率后无缝拼接成全新叙事顺序的视频。

EDL JSON 示例:
[
  {"file": "ep05.mp4", "start": 142.0, "end": 149.5, "note": "黄金前3秒高光钩子"},
  {"file": "ep01.mp4", "start": 5.0, "end": 28.0, "note": "世界观设定引入"},
  {"file": "ep05.mp4", "start": 120.0, "end": 165.0, "note": "高潮正片展开"}
]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile


def main() -> None:
    parser = argparse.ArgumentParser(description="按 EDL JSON 非线性重组/跨源拼接视频片段")
    parser.add_argument("edl_json", help="EDL JSON 文件路径")
    parser.add_argument("output", help="输出拼接后的视频路径")
    parser.add_argument("--size", default="1920x1080", help="统一输出分辨率 WxH，竖屏可传 1080x1920")
    parser.add_argument("--fps", type=int, default=30, help="统一帧率，默认 30")
    parser.add_argument("--encoder", default="h264_videotoolbox", help="视频编码器，默认 h264_videotoolbox")
    parser.add_argument("--bitrate", default="5200k", help="视频码率")
    args = parser.parse_args()

    with open(args.edl_json, "r", encoding="utf-8") as f:
        clips = json.load(f)

    if not clips:
        print("Error: EDL JSON is empty", file=sys.stderr)
        sys.exit(1)

    w, h = [int(x) for x in args.size.lower().split("x")]

    with tempfile.TemporaryDirectory(prefix="dedup_edl_") as tmpdir:
        seg_files = []
        for idx, c in enumerate(clips):
            src = c["file"]
            start = float(c["start"])
            end = float(c["end"])
            dur = end - start
            if dur <= 0:
                raise ValueError(f"Clip #{idx} invalid duration: start={start}, end={end}")
            if not os.path.exists(src):
                raise FileNotFoundError(f"Source file not found: {src}")

            seg_out = os.path.join(tmpdir, f"seg_{idx:03d}.mp4")
            vf = (
                f"fps={args.fps},"
                f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"
            )
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{start:.3f}",
                "-t", f"{dur:.3f}",
                "-i", src,
                "-map_metadata", "-1",
                "-vf", vf,
                "-af", "aresample=48000",
                "-c:v", args.encoder,
            ]
            if args.encoder == "h264_videotoolbox":
                cmd += ["-profile:v", "high", "-b:v", args.bitrate]
            else:
                cmd += ["-preset", "fast", "-crf", "19"]
            cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", seg_out]
            print(f"[{idx+1}/{len(clips)}] Rendering {src} ({start:.2f}s -> {end:.2f}s) {c.get('note', '')}")
            subprocess.run(cmd, check=True)
            seg_files.append(seg_out)

        concat_txt = os.path.join(tmpdir, "concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for sf in seg_files:
                f.write(f"file '{sf}'\n")

        merge_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_txt,
            "-map_metadata", "-1",
            "-c", "copy",
            "-movflags", "+faststart",
            args.output,
        ]
        subprocess.run(merge_cmd, check=True)
        print(f"Concatenated {len(seg_files)} segments -> {args.output}")


if __name__ == "__main__":
    main()
