from dataclasses import dataclass
from typing import Literal


@dataclass
class SyncLaunchResult:
    status: Literal["started", "already_running"]
