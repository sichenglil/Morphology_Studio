"""Generate a deterministic SHA256SUMS.txt for release artifacts."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: generate_checksums.py ARTIFACT_DIR OUTPUT")
    root = Path(sys.argv[1])
    output = Path(sys.argv[2])
    artifacts = sorted(
        path
        for path in root.iterdir()
        if path.is_file()
        and not path.name.endswith(".sha256")
        and path.resolve() != output.resolve()
    )
    if not artifacts:
        raise RuntimeError(f"No release artifacts found in {root}")
    lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in artifacts]
    output.write_text("\n".join(lines) + "\n", encoding="ascii")
    print(f"CHECKSUMS_OK {len(artifacts)} {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
