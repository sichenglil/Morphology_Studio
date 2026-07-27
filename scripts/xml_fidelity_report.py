from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from morphology_toolkit.exporters.urdf_exporter import UrdfExporter
from morphology_toolkit.importers import UrdfImporter


def counts(path: Path):
    root = ET.parse(path).getroot()
    known = {"link", "joint", "material"}
    return Counter(child.tag.rsplit("}", 1)[-1] for child in root if child.tag.rsplit("}", 1)[-1] not in known)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("inputs", nargs="+", type=Path); parser.add_argument("--json", type=Path, required=True); parser.add_argument("--markdown", type=Path, required=True); args = parser.parse_args()
    records = []
    for source in args.inputs:
        target = source.with_suffix(".roundtrip.urdf"); UrdfExporter().export(UrdfImporter().execute(source), target)
        before, after = counts(source), counts(target)
        records.append({"source": source.as_posix(), "before": dict(before), "after": dict(after), "preserved": before == after})
    args.json.parent.mkdir(parents=True, exist_ok=True); args.json.write_text(json.dumps(records, indent=2), encoding="utf-8")
    args.markdown.write_text("# XML round-trip fidelity\n\n" + "\n".join(f"- `{r['source']}`: preserved=`{r['preserved']}`, extensions={r['before']}" for r in records) + "\n", encoding="utf-8")
    print(json.dumps(records))
    return 0 if all(record["preserved"] for record in records) else 2


if __name__ == "__main__": raise SystemExit(main())
