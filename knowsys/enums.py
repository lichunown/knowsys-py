import enum


class CategoryType(enum.Enum):
    Entity = "Entity"
    Relation = "Relation"
    Unknown = "Unknown"


class GroupType(enum.Enum):
    GROUPED: str = 'GROUPED'
    UNGROUPED: str = 'UNGROUPED'


class Direction(enum.Enum):
    FORWARD = 1
    BACKWARD = 2
    BI_DIRECTION = 3
    UNKNOWN = 0

    def contains(self, direction) -> bool:
        """
        BI_DIRECTION contains FORWARD and BACKWARD
        FORWARD not contains BI_DIRECTION

        :param direction:
        :return:
        """
        if self == Direction.BI_DIRECTION:
            return True
        if self == Direction.UNKNOWN:
            return False
        if direction == Direction.UNKNOWN:
            return True
        if direction == Direction.BI_DIRECTION:
            return False
        return self == direction

    def __neg__(self):
        if self == Direction.FORWARD:
            return Direction.BACKWARD
        elif self == Direction.BACKWARD:
            return Direction.FORWARD
        return self

    @classmethod
    def from_str(cls, name):
        return {
            '双向': Direction.BI_DIRECTION,
            '正向': Direction.FORWARD,
            '反向': Direction.BACKWARD,
        }.get(name, Direction.UNKNOWN)


# class CategoryType(enum.Enum):
#     EntityType = "EntityType"
#     RelationType = "RelationType"
#     Unknown = "Unknown"


# class Direction(enum.Enum):
#     FORWARD = 1
#     BACKWARD = 2
#     BI_DIRECTION = 3
#     UNKNOWN = 0
#
#     def contains(self, direction) -> bool:
#         """
#         BI_DIRECTION contains FORWARD and BACKWARD
#         FORWARD not contains BI_DIRECTION
#
#         :param direction:
#         :return:
#         """
#         if self == Direction.BI_DIRECTION:
#             return True
#         if self == Direction.UNKNOWN:
#             return False
#         if direction == Direction.UNKNOWN:
#             return True
#         if direction == Direction.BI_DIRECTION:
#             return False
#         return self == direction
#
#     def __neg__(self):
#         if self == Direction.FORWARD:
#             return Direction.BACKWARD
#         elif self == Direction.BACKWARD:
#             return Direction.FORWARD
#         return self
#
#     @classmethod
#     def from_str(cls, name):
#         return {
#             '双向': Direction.BI_DIRECTION,
#             '正向': Direction.FORWARD,
#             '反向': Direction.BACKWARD,
#         }.get(name, Direction.UNKNOWN)


class CheckingStatus(enum.Enum):
    UN_CHECKED = 'UN_CHECKED'
    REJECT = 'REJECT'
    ACCEPT = 'REJECT'

# class ExternType(enum.Enum):
#     Meta = 'Meta'
#     Term = 'Term'
#
#
# class GroupType(enum.Enum):
#     GROUPED: str = 'GROUPED'
#     UNGROUPED: str = 'UNGROUPED'
