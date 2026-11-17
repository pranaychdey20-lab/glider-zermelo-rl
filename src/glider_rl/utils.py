"""Small shared helpers: config loading, paths, angles, statistics."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "default.yaml"
RESULTS_DIR = REPO_ROOT / "results"


def load_config(path: str | Path | None = None, overrides: Iterable[str] = ()) -> dict[str, Any]:
    """Load a YAML config and apply ``a.b.c=value`` overrides (values parsed as YAML)."""
    with open(path or DEFAULT_CONFIG, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    for item in overrides:
        key, value = item.split("=", 1)
        set_by_path(cfg, key, yaml.safe_load(value))
    return cfg


def set_by_path(cfg: dict[str, Any], dotted: str, value: Any) -> None:
    """Set ``cfg['a']['b']`` from a dotted key ``'a.b'``; the key must already exist."""
    node = cfg
    parts = dotted.split(".")
    for p in parts[:-1]:
        node = node[p]
    if parts[-1] not in node:
        raise KeyError(f"unknown config key {dotted}")
    node[parts[-1]] = value


def with_overrides(cfg: dict[str, Any], **dotted: Any) -> dict[str, Any]:
    """Return a deep copy of ``cfg`` with dotted overrides (use '__' for '.')."""
    out = copy.deepcopy(cfg)
    for k, v in dotted.items():
        set_by_path(out, k.replace("__", "."), v)
    return out


def wrap_angle(a: float | np.ndarray) -> float | np.ndarray:
    """Wrap angle(s) to [-pi, pi)."""
    return (np.asarray(a) + np.pi) % (2 * np.pi) - np.pi


def split_seeds(cfg: dict[str, Any], split: str) -> np.ndarray:
    """Return all map seeds of a split (inclusive range from the config)."""
    lo, hi = cfg["splits"][split]
    return np.arange(lo, hi + 1)


def bootstrap_ci(values: np.ndarray, n_boot: int = 2000, seed: int = 0,
                 stat=np.mean, alpha: float = 0.05) -> tuple[float, float]:
    """Percentile bootstrap CI of ``stat`` over the first axis (maps)."""
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    if values.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, values.size, size=(n_boot, values.size))
    stats = stat(values[idx], axis=1)
    return float(np.quantile(stats, alpha / 2)), float(np.quantile(stats, 1 - alpha / 2))
