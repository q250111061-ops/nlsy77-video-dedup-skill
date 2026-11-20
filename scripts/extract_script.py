#!/usr/bin/env python3
"""
提取视频语音文案与句级时间戳（供语义去重“增删改”与高光重组选段使用）
依赖 faster_whisper。
"""

import argparse
import json
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="提取视频语音逐句文案与时间戳")
    parser.add_argument("input", help="输入音视频路径")
    parser.add_argument("output_json", help="输出 JSON 路径")
    parser.add_argument("--lang", default=None, help="语言代码，如 zh / ja / en（默认自动检测）")
    parser.add_argument("--model", default="small", help="Whisper 模型大小，默认 small")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    from faster_whisper import WhisperModel

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        args.input,
        language=args.lang,
        beam_size=3,
        vad_filter=True,
    )

    items = []
    for idx, seg in enumerate(segments):
        items.append({
            "index": idx,
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump({
            "file": os.path.abspath(args.input),
            "language": info.language,
            "segments": items,
        }, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(items)} segments (lang={info.language}) -> {args.output_json}")


if __name__ == "__main__":
    main()
