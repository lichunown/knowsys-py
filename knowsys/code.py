import abc
import enum
import logging

from typing import *
from knowsys.enums import Direction, CategoryType, GroupType


class Code(abc.ABC):

    @classmethod
    def of(cls, code: str):
        return V1Code(code)

    _entity_type_map = {
        0: 'Unknown',
        1: '人',
        2: '地',
        3: '事',
        4: '物',
        5: '组织',
    }

    def __init__(self):
        self.is_property: Optional[bool] = None
        self.is_group: Optional[bool] = None
        self.is_term: Optional[bool] = None
        self.category_type: CategoryType = CategoryType.Unknown

        self.category_id: int = 0
        self.relation_id: int = 0
        self.property_id: int = 0
        self.extern_l1_id: int = 0
        self.extern_l2_id: int = 0

        self.direction: Direction = Direction.UNKNOWN

    @property
    def from_entity_id(self):
        if self.category_type == CategoryType.Relation:
            return self.category_id // 10

    @property
    def to_entity_id(self):
        if self.category_type == CategoryType.Relation:
            return self.category_id % 10

    @property
    def name(self):
        if self.category_type == CategoryType.Entity:
            return f'<实体（{self._entity_type_map[self.category_id]}）>'
        elif self.category_type == CategoryType.Relation:
            return f'<关系（{self._entity_type_map[self.from_entity_id]}-{self._entity_type_map[self.to_entity_id]}）>'
        else:
            return f'<未知编码>'

    def __repr__(self):
        def _change_to_str(flag: Optional[bool]):
            if flag is None:
                return 'U'
            return 'Y' if flag else 'N'

        return self.name + (f':(prop: {_change_to_str(self.is_property)}, group: {_change_to_str(self.is_group)}, '
                            f'term: {_change_to_str(self.is_term)})')


class V1Code(Code):

    __version__ = 1

    @staticmethod
    def _parse_flag(value: int, true_flag: int, false_flag: int):
        t = value & true_flag
        f = value & false_flag
        if t and f:
            raise ValueError
        if not t and not f:
            return None
        if t:
            return True
        return False

    @staticmethod
    def _flag_to_int(flag: Optional[bool]):
        if flag is None:
            return 0
        if flag:
            return 0b10
        return 0b01

    def __init__(self, code: Union[str, List[bytes]]):
        super().__init__()

        if isinstance(code, List) and isinstance(code[0], bytes):
            raise NotImplementedError

        if not isinstance(code, str):
            raise ValueError

        if len(code) != 16:
            raise ValueError(f'code `{code}` is not a version 1 code.')

        type_code = int(code[2:4], 16)
        self.is_property = self._parse_flag(type_code, 0b00100000, 0b00010000)
        self.is_group = self._parse_flag(type_code, 0b00001000, 0b00000100)
        self.is_term = self._parse_flag(type_code, 0b00000010, 0b00000001)

        if type_code & 0b10000000 and type_code & 0b01000000:
            raise ValueError('a code annot be both a relation and a entity')
        if type_code & 0b10000000:
            self.category_type = CategoryType.Relation
        if type_code & 0b01000000:
            self.category_type = CategoryType.Entity

        self.category_id = int(code[4:6])
        self.relation_id = int(code[6:8], 16)

        if self.category_type == CategoryType.Relation:
            self.direction = {
                '0': Direction.UNKNOWN,
                '1': Direction.FORWARD,
                '2': Direction.BACKWARD,
                '3': Direction.BI_DIRECTION
            }[code[8]]
            self.property_id = int(code[9:11], 16) & 0b00111111
        else:
            self.property_id = int(code[8:11], 16)

        self.extern_l1_id = int(code[11:13], 16)
        self.extern_l2_id = int(code[13:15], 16)

        if self.checking_code != code[-1]:
            logging.warning(f'code: {code} checking fail.')

    @property
    def checking_code(self):
        return hex(int(self._code_without_checking, 16) % 13)[2:]

    @staticmethod
    def hex_padding(value, length=2) -> str:
        v = hex(value)[2:]
        padding_length = length - len(v)
        return '0' * padding_length + v

    @staticmethod
    def padding(v: str, length=2) -> str:
        padding_length = length - len(v)
        return '0' * padding_length + v

    @property
    def string(self):
        return self._code_without_checking + self.checking_code

    @property
    def _code_without_checking(self):
        magic_str = '10'

        flag = {
            CategoryType.Entity: 0b01,
            CategoryType.Relation: 0b10,
            CategoryType.Unknown: 0b00
        }[self.category_type]

        flag_value = ((flag << 6) + (self._flag_to_int(self.is_property) << 4) +
                      (self._flag_to_int(self.is_group) << 2) + self._flag_to_int(self.is_term))
        flag_str = self.hex_padding(flag_value)

        type_str = self.padding(str(self.category_id), 2)
        relation_str = self.hex_padding(self.relation_id)

        if self.category_type == CategoryType.Relation:
            direction_str = {
                Direction.UNKNOWN: '0',
                Direction.FORWARD: '1',
                Direction.BACKWARD: '2',
                Direction.BI_DIRECTION: '3'
            }[self.direction]
            property_str = direction_str + self.hex_padding(self.property_id, 2)
        else:
            property_str = self.hex_padding(self.property_id, 3)

        extern_l1_str = self.hex_padding(self.extern_l1_id, 2)
        extern_l2_str = self.hex_padding(self.extern_l2_id, 2)

        return magic_str + flag_str + type_str + relation_str + property_str + extern_l1_str + extern_l2_str

