from dataclasses import dataclass


@dataclass
class LoadModelRequest:
    model_id: str
