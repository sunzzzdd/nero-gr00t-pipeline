#!/usr/bin/env python3
"""Merge two LeRobot datasets: nero_red_block (68 eps) + nero_red_block2 (40 eps) -> nero_red_block_merged (108 eps)."""

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

# ── Configuration ──────────────────────────────────────────────
BASE = Path("/home/gg/teleop/data/lerobot/local")
SRC1 = BASE / "nero_red_block"       # 68 episodes (0-67)
SRC2 = BASE / "nero_red_block2"      # 40 episodes (0-39)
DST  = BASE / "nero_red_block_merged"

N1 = 68          # dataset1 episode count
N2 = 40          # dataset2 episode count
TOTAL_EPISODES = N1 + N2  # 108

FRAMES1 = 19516  # dataset1 total frames
FRAMES2 = 11104  # dataset2 total frames
TOTAL_FRAMES = FRAMES1 + FRAMES2  # 30620

TOTAL_VIDEOS = TOTAL_EPISODES * 2  # 216 (2 cameras per episode)

UNIFIED_TASK = "Pick up the red block and place it on the other side"

CAMERAS = ["observation.images.cam_high", "observation.images.cam_right_wrist"]


# ── Helpers ────────────────────────────────────────────────────
def load_jsonl(path):
    """Load a JSONL file into a list of dicts."""
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def write_jsonl(path, items):
    """Write a list of dicts to a JSONL file."""
    with open(path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


def combine_parallel_stats(s1, s2):
    """Combine two sets of stats (dicts with min/max/mean/std/count) using the parallel algorithm.

    Works for both scalar (1-element lists) and nested (image) stats.
    Uses population std (ddof=0), consistent with LeRobot's convention.
    """
    a1 = np.array(s1["mean"], dtype=float)
    a2 = np.array(s2["mean"], dtype=float)
    std1 = np.array(s1["std"], dtype=float)
    std2 = np.array(s2["std"], dtype=float)
    c1 = s1["count"][0]
    c2 = s2["count"][0]
    ct = c1 + c2

    combined_mean = (a1 * c1 + a2 * c2) / ct
    var1 = std1 ** 2
    var2 = std2 ** 2
    combined_var = (c1 * (var1 + (a1 - combined_mean) ** 2) +
                    c2 * (var2 + (a2 - combined_mean) ** 2)) / ct
    combined_std = np.sqrt(combined_var)

    min1 = np.array(s1["min"])
    min2 = np.array(s2["min"])
    max1 = np.array(s1["max"])
    max2 = np.array(s2["max"])

    return {
        "min": np.minimum(min1, min2).tolist(),
        "max": np.maximum(max1, max2).tolist(),
        "mean": combined_mean.tolist(),
        "std": combined_std.tolist(),
        "count": [ct],
    }


# ── Main merge steps ───────────────────────────────────────────
def create_dirs():
    """Create the output directory structure."""
    if DST.exists():
        shutil.rmtree(DST)
    for sub in [
        "data/chunk-000",
        "meta",
        "videos/chunk-000/observation.images.cam_high",
        "videos/chunk-000/observation.images.cam_right_wrist",
    ]:
        (DST / sub).mkdir(parents=True, exist_ok=True)


def copy_parquet():
    """Copy parquet files: dataset1 as-is, dataset2 with updated episode_index and index."""
    # Dataset1: straight copy (episode_index 0-67, index 0-19515)
    for i in range(N1):
        src = SRC1 / f"data/chunk-000/episode_{i:06d}.parquet"
        dst = DST  / f"data/chunk-000/episode_{i:06d}.parquet"
        shutil.copy2(src, dst)

    # Dataset2: update episode_index (→ 68-107) and index (offset +19516)
    for i in range(N2):
        src = SRC2 / f"data/chunk-000/episode_{i:06d}.parquet"
        dst = DST  / f"data/chunk-000/episode_{i + N1:06d}.parquet"
        table = pq.read_table(src)

        # episode_index += N1
        new_ep = pc.add(table.column("episode_index"), N1)
        table = table.set_column(
            table.schema.get_field_index("episode_index"),
            table.schema.field("episode_index"),
            new_ep,
        )

        # index += FRAMES1 (global frame offset)
        new_idx = pc.add(table.column("index"), FRAMES1)
        table = table.set_column(
            table.schema.get_field_index("index"),
            table.schema.field("index"),
            new_idx,
        )

        # task_index stays 0 (already 0 in both datasets)
        # Write preserving original schema metadata
        pq.write_table(table, dst)

    print(f"  Parquet: {N1} (copied) + {N2} (remapped) = {TOTAL_EPISODES} files")


def copy_videos():
    """Copy video files: dataset1 as-is, dataset2 with renamed episode numbers."""
    for cam in CAMERAS:
        # Dataset1: straight copy
        for i in range(N1):
            src = SRC1 / f"videos/chunk-000/{cam}/episode_{i:06d}.mp4"
            dst = DST  / f"videos/chunk-000/{cam}/episode_{i:06d}.mp4"
            if src.exists():
                shutil.copy2(src, dst)

        # Dataset2: rename episode_{i} → episode_{i+68}
        for i in range(N2):
            src = SRC2 / f"videos/chunk-000/{cam}/episode_{i:06d}.mp4"
            dst = DST  / f"videos/chunk-000/{cam}/episode_{i + N1:06d}.mp4"
            if src.exists():
                shutil.copy2(src, dst)

    print(f"  Videos: {TOTAL_VIDEOS} files ({len(CAMERAS)} cameras × {TOTAL_EPISODES} episodes)")


def merge_episodes_jsonl():
    """Merge episodes.jsonl: unify task description, remap dataset2 episode_index."""
    episodes = []

    # Dataset1: update task description to unified
    for ep in load_jsonl(SRC1 / "meta/episodes.jsonl"):
        ep["tasks"] = [UNIFIED_TASK]
        episodes.append(ep)

    # Dataset2: update episode_index and task description
    for ep in load_jsonl(SRC2 / "meta/episodes.jsonl"):
        ep["episode_index"] = ep["episode_index"] + N1
        ep["tasks"] = [UNIFIED_TASK]
        episodes.append(ep)

    write_jsonl(DST / "meta/episodes.jsonl", episodes)
    print(f"  episodes.jsonl: {len(episodes)} entries")


def update_info_json():
    """Update info.json with merged totals."""
    with open(SRC1 / "meta/info.json") as f:
        info = json.load(f)

    info["total_episodes"] = TOTAL_EPISODES
    info["total_frames"]   = TOTAL_FRAMES
    info["total_videos"]   = TOTAL_VIDEOS
    info["total_tasks"]    = 1
    info["splits"]         = {"train": f"0:{TOTAL_EPISODES}"}

    with open(DST / "meta/info.json", "w") as f:
        json.dump(info, f, indent=4)
    print(f"  info.json: episodes={TOTAL_EPISODES}, frames={TOTAL_FRAMES}, videos={TOTAL_VIDEOS}")


def update_tasks_jsonl():
    """Write unified tasks.jsonl."""
    with open(DST / "meta/tasks.jsonl", "w") as f:
        f.write(json.dumps({"task_index": 0, "task": UNIFIED_TASK}) + "\n")
    print(f"  tasks.jsonl: unified → '{UNIFIED_TASK}'")


def copy_modality_json():
    """Copy modality.json (identical in both datasets, right_gripper [7:8] confirmed)."""
    shutil.copy2(SRC1 / "meta/modality.json", DST / "meta/modality.json")
    print("  modality.json: copied (right_gripper [7:8] confirmed)")


def recalculate_stats():
    """Recalculate global stats.json from merged parquet data + combined image stats."""
    # Read all parquet tables and concat
    tables = []
    for i in range(TOTAL_EPISODES):
        f = DST / f"data/chunk-000/episode_{i:06d}.parquet"
        tables.append(pq.read_table(f))
    combined = pa.concat_tables(tables)
    df = combined.to_pandas()

    stats = {}

    # ── Vector fields (observation.state, action) ──
    for field in ["observation.state", "action"]:
        arr = np.stack(df[field].values)  # (N, 8)
        stats[field] = {
            "min":   arr.min(axis=0).tolist(),
            "max":   arr.max(axis=0).tolist(),
            "mean":  arr.mean(axis=0).tolist(),
            "std":   arr.std(axis=0).tolist(),   # population std (ddof=0)
            "count": [len(arr)],
        }

    # ── Scalar integer fields ──
    for field in ["frame_index", "episode_index", "index", "task_index"]:
        arr = df[field].to_numpy()
        stats[field] = {
            "min":   [int(arr.min())],
            "max":   [int(arr.max())],
            "mean":  [float(arr.mean())],
            "std":   [float(arr.std())],
            "count": [len(arr)],
        }

    # ── Scalar float field (timestamp) ──
    arr_ts = df["timestamp"].to_numpy()
    stats["timestamp"] = {
        "min":   [float(arr_ts.min())],
        "max":   [float(arr_ts.max())],
        "mean":  [float(arr_ts.mean())],
        "std":   [float(arr_ts.std())],
        "count": [len(arr_ts)],
    }

    # ── Image fields: combine original stats via parallel algorithm ──
    with open(SRC1 / "meta/stats.json") as f:
        stats1 = json.load(f)
    with open(SRC2 / "meta/stats.json") as f:
        stats2 = json.load(f)

    for img_field in ["observation.images.cam_high", "observation.images.cam_right_wrist"]:
        stats[img_field] = combine_parallel_stats(stats1[img_field], stats2[img_field])

    with open(DST / "meta/stats.json", "w") as f:
        json.dump(stats, f, indent=4)
    print("  stats.json: recalculated (scalar from parquet, image via parallel combine)")


def merge_episodes_stats():
    """Merge episodes_stats.jsonl: dataset1 as-is, dataset2 with remapped episode_index and index."""
    all_stats = []

    # Dataset1: copy as-is
    for item in load_jsonl(SRC1 / "meta/episodes_stats.jsonl"):
        all_stats.append(item)

    # Dataset2: remap episode_index and index stats
    for item in load_jsonl(SRC2 / "meta/episodes_stats.jsonl"):
        old_ep = item["episode_index"]
        new_ep = old_ep + N1
        item["episode_index"] = new_ep

        s = item["stats"]

        # Update episode_index stats
        if "episode_index" in s:
            s["episode_index"]["min"]  = [new_ep]
            s["episode_index"]["max"]  = [new_ep]
            s["episode_index"]["mean"] = [float(new_ep)]
            # std stays 0.0

        # Update index stats (global frame index offset)
        if "index" in s:
            s["index"]["min"]  = [s["index"]["min"][0]  + FRAMES1]
            s["index"]["max"]  = [s["index"]["max"][0]  + FRAMES1]
            s["index"]["mean"] = [s["index"]["mean"][0] + FRAMES1]
            # std stays the same

        all_stats.append(item)

    write_jsonl(DST / "meta/episodes_stats.jsonl", all_stats)
    print(f"  episodes_stats.jsonl: {len(all_stats)} entries")


def merge_episode_list():
    """Merge episode_list.txt (concatenate both lists)."""
    lines = []
    with open(SRC1 / "meta/episode_list.txt") as f:
        lines.extend(f.read().strip().split("\n"))
    with open(SRC2 / "meta/episode_list.txt") as f:
        lines.extend(f.read().strip().split("\n"))

    with open(DST / "meta/episode_list.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  episode_list.txt: {len(lines)} entries")


# ── Entry point ────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Merging LeRobot datasets")
    print(f"  Source 1: {SRC1}  ({N1} episodes, {FRAMES1} frames)")
    print(f"  Source 2: {SRC2}  ({N2} episodes, {FRAMES2} frames)")
    print(f"  Target:   {DST}  ({TOTAL_EPISODES} episodes, {TOTAL_FRAMES} frames)")
    print("=" * 60)

    print("\n[1/10] Creating directory structure...")
    create_dirs()

    print("\n[2/10] Copying parquet files...")
    copy_parquet()

    print("\n[3/10] Copying video files...")
    copy_videos()

    print("\n[4/10] Merging episodes.jsonl...")
    merge_episodes_jsonl()

    print("\n[5/10] Updating info.json...")
    update_info_json()

    print("\n[6/10] Updating tasks.jsonl...")
    update_tasks_jsonl()

    print("\n[7/10] Copying modality.json...")
    copy_modality_json()

    print("\n[8/10] Recalculating stats.json...")
    recalculate_stats()

    print("\n[9/10] Merging episodes_stats.jsonl...")
    merge_episodes_stats()

    print("\n[10/10] Merging episode_list.txt...")
    merge_episode_list()

    print("\n" + "=" * 60)
    print("Merge complete!")
    print(f"  Episodes: {TOTAL_EPISODES}")
    print(f"  Frames:   {TOTAL_FRAMES}")
    print(f"  Videos:   {TOTAL_VIDEOS}")
    print(f"  Output:   {DST}")
    print("=" * 60)


if __name__ == "__main__":
    main()
