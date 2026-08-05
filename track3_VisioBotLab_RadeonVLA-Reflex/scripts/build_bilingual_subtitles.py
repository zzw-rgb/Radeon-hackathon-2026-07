#!/usr/bin/env python3
# ruff: noqa: E501
"""Stitch Edge-TTS subtitle parts and add reviewed Simplified-Chinese lines."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

TRANSLATIONS = {
    "When a vision-language-action model predicts an action chunk, the world can change before it finishes.": "当视觉语言动作模型预测一个动作块时，环境可能在执行完成前发生变化。",
    "A missed grasp or a new command can make every remaining action stale.": "一次抓取失败或一条新指令，都可能让剩余动作全部过期。",
    "Radeon V L A Reflex makes execution interruptible, failure-aware, and recoverable.": "RadeonVLA-Reflex 让执行可以中断、感知失败并安全恢复。",
    "Our testbed is language-guided fruit sorting with a Franka robot in Genesis.": "我们的测试台是在 Genesis 中由语言引导 Franka 机械臂分拣水果。",
    "Five fruits and four language-addressable bowls form twenty registered tasks with exact, auditable instructions.": "五种水果与四个语言可指定碗构成二十项注册任务，指令精确且可审计。",
    "Smol V L A receives world and wrist cameras, nine-dimensional robot state, and natural language.": "SmolVLA 接收世界相机、腕部相机、九维机器人状态和自然语言。",
    "It predicts joint-position actions for the arm and gripper.": "模型为机械臂和夹爪预测关节位置动作。",
    "Every action passes joint-limit and rate checks before execution.": "每个动作执行前都经过关节限位与速率检查。",
    "Each command carries a version number.": "每条指令都带有版本号。",
    "If the operator changes the destination, the old chunk is invalidated immediately.": "当操作者改变目标时，旧动作块立即失效。",
    "The robot holds safely, clears cached actions, and starts the new command without completing revoked intent.": "机器人安全保持、清空缓存动作并执行新指令，不再完成已撤销的意图。",
    "Training uses our Physical Two K release: two thousand successful episodes and four hundred sixty-eight thousand eight hundred eighty-nine frames.": "训练采用 Physical-2K：两千条成功轨迹，共四十六万八千八百八十九帧。",
    "Each of the twenty tasks has one hundred demonstrations, independent seeds, and strict-physics certificates.": "二十项任务各有一百条演示、独立 seed 与严格物理证书。",
    "Kinematic grasp attachment, object teleportation, and placement nudges are disabled.": "运动学抓取粘附、物体瞬移和放置微调均被禁用。",
    "Runtime guards reject rigid-body pose writes.": "运行时防护拒绝刚体位姿写入。",
    "All two thousand certificates pass with zero errors and zero warnings.": "两千份证书全部通过，错误和警告均为零。",
    "Simulation, collection, training, and evaluation run on one AMD Radeon GPU.": "仿真、采集、训练和评测都运行在一张 AMD Radeon GPU 上。",
    "The stack uses ROCm seven point two, PyTorch two point nine point one, Genesis one point one point two, and LeRobot zero point six.": "软件栈采用 ROCm 7.2、PyTorch 2.9.1、Genesis 1.1.2 与 LeRobot 0.6。",
    "Training reaches about two hundred thousand cumulative steps.": "模型累计训练约二十万步。",
    "The final one-hundred-thousand-step continuation takes three hours and forty-five minutes at about thirty samples per second.": "最后十万步续训耗时三小时四十五分钟，速度约每秒三十个样本。",
    "Peak training memory is two point two two gigabytes, and final loss is zero point zero five eight.": "训练峰值显存为 2.22 GB，最终损失为 0.058。",
    "Watch the learned controller approach, grasp, lift, transport, and release.": "观察学习控制器完成接近、抓取、抬升、搬运与释放。",
    "Success counts only when the correct fruit settles inside the requested bowl.": "只有正确水果稳定落入指定碗中才计为成功。",
    "No post-processing moves the object after release.": "释放后不会通过任何后处理移动物体。",
    "After an empty grasp, Precision Reflex runs bounded geometric recovery under the same strict-physics restrictions.": "空抓后，Precision Reflex 在同样的严格物理约束下执行有界几何恢复。",
    "Learned first-attempt success and deterministic recovery are always reported separately.": "学习策略首次成功与确定性恢复始终分开报告。",
    "The formal benchmark freezes one model hash and tests all twenty tasks with five disjoint seeds each.": "正式基准固定同一模型哈希，对二十项任务各测试五个互不重叠的 seed。",
    "Learned control succeeds first on thirty-six rollouts.": "学习控制在三十六次评测中首次成功。",
    "Precision Reflex recovers fifty-five more, producing ninety-one successes out of one hundred.": "Precision Reflex 再恢复五十五次，最终一百次中成功九十一次。",
    "The ninety-five-percent Wilson interval is eighty-three point eight to ninety-five point two percent.": "95% Wilson 置信区间为 83.8% 到 95.2%。",
    "Inference latency is four point five four milliseconds at the median and thirty-seven point two seven at P ninety-five.": "推理延迟中位数为 4.54 毫秒，P95 为 37.27 毫秒。",
    "All nine failures remain public.": "九次失败全部保留并公开。",
    "An independent probe switches an apple from the white-left bowl to the blue-right bowl at step forty.": "独立测试在第 40 步把苹果目标从左侧白碗改为右侧蓝碗。",
    "The stale chunk stops with zero old-command actions.": "过期动作块停止后，旧指令动作泄漏为零。",
    "After the learned continuation empty-grasps, a labeled strict-physics recovery completes the new target.": "学习控制继续执行但发生空抓，随后由明确标注的严格物理恢复完成新目标。",
    "Source, Physical Two K, weights, evaluation videos, checksums, report, and the interactive evidence console are public.": "源码、Physical-2K、权重、评测视频、校验和、报告与交互证据控制台均已公开。",
    "Results cover Genesis simulation only, with no real-robot claim.": "结果仅覆盖 Genesis 仿真，不作真机声明。",
    "Radeon V L A Reflex shows that a useful V L A system must know how to act, when to stop, and how to recover safely.": "RadeonVLA-Reflex 表明，实用的 VLA 系统既要会行动，也要知道何时停止并安全恢复。",
}

BLOCK_RE = re.compile(
    r"\d+\s*\n(\d\d:\d\d:\d\d,\d{3})\s+-->\s+(\d\d:\d\d:\d\d,\d{3})\s*\n(.+?)(?=\n\n|\Z)",
    re.DOTALL,
)


def to_ms(value: str) -> int:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return ((int(hours) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(millis)


def from_ms(value: int) -> str:
    hours, remainder = divmod(max(0, value), 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def duration_ms(path: Path) -> int:
    output = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nk=1:nw=1",
            str(path),
        ],
        text=True,
    )
    return round(float(output.strip()) * 1000)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parts_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--target-duration", type=float, default=None)
    args = parser.parse_args()

    audio_parts = sorted(args.parts_dir.glob("*.mp3"))
    if not audio_parts:
        raise FileNotFoundError(f"No MP3 parts found in {args.parts_dir}")

    offset = 0
    cues: list[tuple[int, int, str]] = []
    for audio_path in audio_parts:
        srt_path = audio_path.with_suffix(".srt")
        text = srt_path.read_text(encoding="utf-8-sig")
        for match in BLOCK_RE.finditer(text):
            english = " ".join(match.group(3).split())
            if english not in TRANSLATIONS:
                raise KeyError(f"Missing reviewed translation: {english}")
            cues.append((offset + to_ms(match.group(1)), offset + to_ms(match.group(2)), english))
        offset += duration_ms(audio_path)

    scale = 1.0 if args.target_duration is None else (args.target_duration * 1000) / offset
    blocks = []
    for index, (start, end, english) in enumerate(cues, start=1):
        blocks.append(
            f"{index}\n{from_ms(round(start * scale))} --> {from_ms(round(end * scale))}\n"
            f"{english}\n{TRANSLATIONS[english]}"
        )
    args.output.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"parts={len(audio_parts)} cues={len(cues)} source_duration_s={offset / 1000:.3f} scale={scale:.6f}")


if __name__ == "__main__":
    main()
