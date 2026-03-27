from dataclasses import dataclass


@dataclass
class DownloadModelRequest:
    repo: str
    filename: str
