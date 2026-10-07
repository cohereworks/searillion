from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.metadata
import json
import os
import platform
import resource
import sys
import time
from typing import Any, Callable


@dataclass(frozen=True)
class Measurement:
    name: str
    wall_seconds: float
    cpu_seconds: float
    peak_rss_kib: int
    python: str
    platform: str
    graphillion: str
    metadata: dict[str, Any]
    result: Any

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, default=str)


def _graphillion_version() -> str:
    try:
        return importlib.metadata.version("graphillion")
    except importlib.metadata.PackageNotFoundError:
        return "uninstalled"


def measure(name: str, fn: Callable[[], Any], **metadata: Any) -> Measurement:
    wall0 = time.perf_counter()
    cpu0 = time.process_time()
    result = fn()
    cpu = time.process_time() - cpu0
    wall = time.perf_counter() - wall0
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return Measurement(
        name=name,
        wall_seconds=wall,
        cpu_seconds=cpu,
        peak_rss_kib=int(rss),
        python=sys.version.split()[0],
        platform=platform.platform(),
        graphillion=_graphillion_version(),
        metadata=metadata,
        result=result,
    )


def write_jsonl(path: str, measurements: list[Measurement]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in measurements:
            f.write(item.to_json() + "\n")
