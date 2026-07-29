from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class StepAdapterStatus:
    available: bool
    root: Path | None
    pnpm: Path | None
    installed: bool
    url: str = "http://127.0.0.1:5173"
    reason: str = ""

    def public_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["root"] = self.root.as_posix() if self.root else None
        payload["pnpm"] = self.pnpm.as_posix() if self.pnpm else None
        return payload


class Step2UrdfAdapter:
    """Discover and launch the separately installed interactive step2urdf UI.

    The upstream application intentionally exposes no batch conversion API: defining
    links and joints requires user decisions. Morphology Studio therefore integrates
    it as an optional local editor and imports its exported URDF ZIP package.
    """

    ENV = "MORPHOLOGY_STEP2URDF_PATH"

    def __init__(self, root: Path | None = None) -> None:
        self._root = Path(root).expanduser() if root else None

    def candidates(self) -> list[Path]:
        values: list[Path] = []
        configured = os.environ.get(self.ENV)
        if self._root:
            values.append(self._root)
        if configured:
            values.append(Path(configured).expanduser())
        values.extend((Path.cwd() / "external" / "step2urdf", Path.cwd() / "step2urdf"))
        result: list[Path] = []
        for value in values:
            resolved = value.resolve()
            if resolved not in result:
                result.append(resolved)
        return result

    def status(self) -> StepAdapterStatus:
        root = next((path for path in self.candidates() if (path / "package.json").is_file()), None)
        pnpm_raw = shutil.which("pnpm")
        pnpm = Path(pnpm_raw).resolve() if pnpm_raw else None
        if root is None:
            return StepAdapterStatus(False, None, pnpm, False, reason=f"Set {self.ENV}")
        installed = (root / "node_modules").is_dir()
        if pnpm is None:
            return StepAdapterStatus(False, root, None, installed, reason="pnpm was not found")
        if not installed:
            return StepAdapterStatus(False, root, pnpm, False, reason="Run pnpm install first")
        return StepAdapterStatus(True, root, pnpm, True)

    def launch(self) -> StepAdapterStatus:
        status = self.status()
        if not status.available or status.root is None or status.pnpm is None:
            raise RuntimeError(status.reason or "step2urdf adapter is unavailable")
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        subprocess.Popen(  # noqa: S603
            [str(status.pnpm), "dev", "--host", "127.0.0.1"],
            cwd=status.root,
            creationflags=flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return status
