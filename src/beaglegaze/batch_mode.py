import enum
import random

class BatchMode(enum.Enum):
    OFF = "OFF"
    RANDOM = "RANDOM"

    def hit(self):
        if self == BatchMode.OFF:
            return True
        elif self == BatchMode.RANDOM:
            return random.random() < 0.1
        else:
            return False
