"""Screen capture abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class ScreenCapture(ABC):
    """Grab BGR frames from a monitor region."""

    @abstractmethod
    def grab(self) -> np.ndarray | None:
        """Return latest BGR frame or None if unavailable."""

    @abstractmethod
    def close(self) -> None:
        """Release capture resources."""
