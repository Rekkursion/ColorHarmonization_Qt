from enum import Enum


# the enum-class of statuses of the image-process
class ProcessStatus(Enum):
    LOADING = 'Loading or waiting'
    LOADED = 'Loaded'
    PROCESSING = 'Processing'
    DONE = 'Done'
    ERROR = 'ERROR happened'

    # get the text-color of the designated process-status
    def get_text_color(self):
        if self == ProcessStatus.LOADING:
            return 67, 142, 243  # orange
        elif self == ProcessStatus.LOADED:
            return 152, 109, 33  # ???
        elif self == ProcessStatus.PROCESSING:
            return 253, 16, 19  # blue
        elif self == ProcessStatus.DONE:
            return 16, 109, 2  # green
        else:  # ERROR
            return 0, 0, 255  # red
