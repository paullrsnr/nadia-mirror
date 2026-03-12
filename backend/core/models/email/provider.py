from enum import Enum


class Provider(str, Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    ALL = "all"
