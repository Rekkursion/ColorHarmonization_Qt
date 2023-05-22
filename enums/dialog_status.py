from enum import Enum


# the enum-class of statuses of dialogs
class DialogStatus(Enum):
    DISPLAYING = 0
    ACCEPTED = 1
    CANCELED = 2
    ERROR = 3
