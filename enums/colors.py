from enum import Enum


class Colors(Enum):
    LOG_GENERAL = (0,) * 3
    
    # the text-color of the log when an image is loaded successfully
    LOG_LOAD_IMAGE = (85, 79, 182)

    # the text-color of the log when the process of an image is done successfully
    LOG_PROCESS_DONE = (177, 91, 46)

    # the text-color of the log when an image or a set of images has been saved
    LOG_IMAGE_SAVED = (107, 191, 146)

    # the text-color of an error-like log
    LOG_ERROR = (244, 61, 22)

    # the text-color of a warning-like log
    LOG_WARNING = (200, 155, 1)

    # for the convenience (no need to write Colors.XXX.value, only Colors.XXX is nice)
    def __get__(self, instance, owner):
        return self.value
