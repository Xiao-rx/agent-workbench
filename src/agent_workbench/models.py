from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileSignal:
    path: str
    kind: str
    lines: int
    bytes: int


@dataclass(frozen=True)
class AgentAsset:
    path: str
    label: str


@dataclass(frozen=True)
class RepoMap:
    root: Path
    files: tuple[FileSignal, ...]
    package_managers: tuple[str, ...]
    test_commands: tuple[str, ...]
    risk_notes: tuple[str, ...]
    agent_assets: tuple[AgentAsset, ...] = ()

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_lines(self) -> int:
        return sum(file.lines for file in self.files)
