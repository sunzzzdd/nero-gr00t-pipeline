#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from lerobot.datasets.compute_stats import aggregate_stats, compute_episode_stats
from lerobot.datasets.utils import (
    DEFAULT_CHUNK_SIZE,
    EPISODES_STATS_PATH,
    load_episodes,
    load_episodes_stats,
    load_info,
    load_stats,
    serialize_dict,
    write_jsonlines,
    write_stats,
)


def normalize_media_paths(values: list[str | None], dataset_dir: Path) -> list[str | None]:
    """Normalize image/video paths to absolute paths."""
    normalized: list[str | None] = []
    for value in values:
        if value in (None, ""):
            normalized.append(value)
            continue
        path = Path(value)
        if not path.is_absolute():
            path = (dataset_dir / path).resolve()
        normalized.append(str(path))
    return normalized


def list_to_numpy(values: list, dtype: str) -> np.ndarray:
    if len(values) == 0:
        return np.empty((0,), dtype=np.dtype(dtype))

    first = next((val for val in values if val is not None), None)
    if first is None:
        return np.asarray(values)

    if isinstance(first, (list, tuple, np.ndarray)):
        stacked = [np.asarray(v, dtype=dtype) for v in values]
        return np.stack(stacked)

    return np.asarray(values, dtype=dtype)


def load_episode_data(
    parquet_path: Path,
    features: dict[str, dict],
    dataset_dir: Path,
) -> dict[str, list | np.ndarray]:
    table = pq.read_table(parquet_path)
    column_names = set(table.column_names)
    episode_data: dict[str, list | np.ndarray] = {}

    for key, ft in features.items():
        if key not in column_names:
            continue
        column = table[key]
        values = column.to_pylist()

        dtype = ft["dtype"]
        if dtype in ["image", "video"]:
            episode_data[key] = normalize_media_paths(values, dataset_dir)
        elif dtype == "string":
            episode_data[key] = values
        else:
            episode_data[key] = list_to_numpy(values, ft["dtype"])

    return episode_data


def save_episode_stats(episodes_stats: dict[int, dict], dataset_dir: Path) -> None:
    records = [
        {"episode_index": ep_idx, "stats": serialize_dict(stats)}
        for ep_idx, stats in sorted(episodes_stats.items())
    ]
    write_jsonlines(records, dataset_dir / EPISODES_STATS_PATH)


def main() -> None:
    args = parse_args()
    dataset_dir = Path(args.datasetDir).expanduser().resolve()
    if not (dataset_dir / "meta" / "info.json").is_file():
        raise FileNotFoundError(f"{dataset_dir} does not contain meta/info.json.")

    info = load_info(dataset_dir)
    episodes = load_episodes(dataset_dir)
    if len(episodes) == 0:
        raise ValueError(f"No episodes found in {dataset_dir}.")

    available_episode_indices = sorted(episodes.keys())
    if args.episodes is None:
        episode_indices = available_episode_indices
    else:
        missing = sorted(set(args.episodes) - set(episodes.keys()))
        if missing:
            raise ValueError(f"Episode indices {missing} are not present in the dataset.")
        episode_indices = sorted(args.episodes)

    chunk_size = info.get("chunks_size", DEFAULT_CHUNK_SIZE)
    data_path_template = info["data_path"]
    features = info["features"]

    # Identify image/video features to preserve
    image_keys = [key for key, ft in features.items() if ft["dtype"] in ["image", "video", "image_path"]]
    
    # Load existing stats to preserve image stats
    old_stats = load_stats(dataset_dir)
    old_episodes_stats = {}
    if (dataset_dir / EPISODES_STATS_PATH).exists():
        try:
            old_episodes_stats = load_episodes_stats(dataset_dir)
        except Exception:
            pass  # If loading fails, use empty dict
    
    if image_keys:
        if old_stats:
            print(f"[compute_stats] Found {len(image_keys)} image/video features. Preserving existing image stats.")
            print(f"[compute_stats] Image features: {image_keys}")
        else:
            print(f"[compute_stats] Found {len(image_keys)} image/video features, but no existing stats found. Will compute new image stats.")

    # Compute stats only for non-image features if we have old stats to preserve
    if old_stats and image_keys:
        features_to_compute = {k: v for k, v in features.items() if k not in image_keys}
    else:
        features_to_compute = features
    
    episodes_stats: dict[int, dict] = {}
    for idx, episode_index in enumerate(episode_indices, start=1):
        chunk = episode_index // chunk_size
        rel_path = data_path_template.format(episode_chunk=chunk, episode_index=episode_index)
        parquet_path = dataset_dir / rel_path
        if not parquet_path.is_file():
            raise FileNotFoundError(f"Missing parquet file for episode {episode_index}: {parquet_path}")
        episode_data = load_episode_data(parquet_path, features, dataset_dir)
        # Compute stats (excluding image features if we're preserving old stats)
        if old_stats and image_keys:
            data_to_compute = {k: v for k, v in episode_data.items() if k not in image_keys}
            episode_stats = compute_episode_stats(data_to_compute, features_to_compute)
            
            # Preserve image stats from old stats if available
            if episode_index in old_episodes_stats:
                for img_key in image_keys:
                    if img_key in old_episodes_stats[episode_index]:
                        episode_stats[img_key] = old_episodes_stats[episode_index][img_key]
        else:
            # Compute all stats including images
            episode_stats = compute_episode_stats(episode_data, features_to_compute)
        
        episodes_stats[episode_index] = episode_stats

        if args.log_interval > 0 and idx % args.log_interval == 0:
            print(f"[compute_stats] Processed {idx} / {len(episode_indices)} episodes.")

    aggregated_stats = aggregate_stats(list(episodes_stats.values()))
    
    # Preserve image stats in aggregated stats from old stats
    if image_keys and old_stats:
        for img_key in image_keys:
            if img_key in old_stats:
                aggregated_stats[img_key] = old_stats[img_key]
                print(f"[compute_stats] Preserved aggregated stats for {img_key}")
    
    write_stats(aggregated_stats, dataset_dir)
    save_episode_stats(episodes_stats, dataset_dir)

    print(
        f"[compute_stats] Completed stats for {len(episode_indices)} episodes. "
        f"Updated files under {dataset_dir / 'meta'}."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recompute per-episode and aggregated stats for a local LeRobot dataset."
    )
    parser.add_argument(
        "--datasetDir",
        required=True,
        help="Path to the dataset root (must contain meta/ and data/).",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        nargs="+",
        default=None,
        help="Optional list of episode indices to process. Defaults to all episodes.",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=10,
        help="Log progress every N processed episodes. Set to 0 to disable.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()

