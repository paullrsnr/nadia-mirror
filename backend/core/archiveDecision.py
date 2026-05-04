from enum import Enum


class ArchiveDecision(str, Enum):
    YES = "oui"
    NO = "non"
    UNCERTAIN = "incertain"
