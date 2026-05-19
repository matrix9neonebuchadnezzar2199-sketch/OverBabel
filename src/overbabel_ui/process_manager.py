"""Spawn vision / audio server child processes."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass

from overbabel_core.utils import get_logger

_log = get_logger("ui.process")


@dataclass
class ManagedProcess:
    name: str
    popen: subprocess.Popen[bytes] | subprocess.Popen[str] | None = None

    def start(self, module: str, *, env: dict[str, str] | None = None) -> None:
        if self.popen is not None and self.popen.poll() is None:
            return
        cmd = [sys.executable, "-m", module]
        self.popen = subprocess.Popen(cmd, env=env)
        _log.info("process.start", name=self.name, cmd=" ".join(cmd))

    def stop(self) -> None:
        if self.popen is None:
            return
        if self.popen.poll() is None:
            self.popen.terminate()
            try:
                self.popen.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.popen.kill()
        _log.info("process.stop", name=self.name)
        self.popen = None
