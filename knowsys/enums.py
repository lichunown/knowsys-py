from enum import IntEnum


class DirectionType(IntEnum):
    UNKNOWN = 0
    BiDirection = 1
    Direction = 2

class Direction(IntEnum):
    Forward = 1
    Backward = -1
    BiDirection = 0

