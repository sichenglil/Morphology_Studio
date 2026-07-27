from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from morphology_toolkit.core.model import ProcessingMode, RobotModel


@dataclass
class Candidate:
    path: Path
    detected_format: str
    score: float
    reason: str
    requires_confirmation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def confidence(self) -> str:
        return "high" if self.score >= 0.8 else "medium" if self.score >= 0.5 else "low"


@dataclass
class ImportAnalysis:
    input_path: Path
    format_candidates: List[Candidate] = field(default_factory=list)
    entry_candidates: List[Candidate] = field(default_factory=list)
    parameter_candidates: Dict[str, Optional[str]] = field(default_factory=dict)
    resource_candidates: List[str] = field(default_factory=list)
    root_candidates: List[str] = field(default_factory=list)
    interface_candidates: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)


class Importer(ABC):
    @abstractmethod
    def analyze(self, path: Path) -> ImportAnalysis: ...

    @abstractmethod
    def execute(
        self,
        path: Path,
        mode: ProcessingMode = ProcessingMode.ASSISTED,
        selection: Optional[Dict[str, Any]] = None,
    ) -> RobotModel: ...
