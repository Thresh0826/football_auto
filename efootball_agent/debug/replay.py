from __future__ import annotations

import json
from pathlib import Path


def replay_file(path: str | Path, config_path: str) -> int:
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(file)
    count = 0
    with file.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            print(f"{item['timestamp']:.3f} state={item['state']['phase']} action={item['decision']['action']} reason={item['decision']['reason']}")
            count += 1
    print(f"replay records: {count}")
    return 0

