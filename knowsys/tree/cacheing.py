import functools
import random
from collections import defaultdict
from typing import *
import logging

from functools import cache

_logger = logging.getLogger('cacheing')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_logger.addHandler(console_handler)


class _HashedSeq(list):
    """ This class guarantees that hash() will be called no more than once
        per element.  This is important because the lru_cache() will hash
        the key multiple times on a cache miss.

    """

    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(args, kwds, typed,
             kwd_mark = (object(),),
             fasttypes = {int, str},
             tuple=tuple, type=type, len=len):
    """Make a cache key from optionally typed positional and keyword arguments

    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.

    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.

    """
    # All of code below relies on kwds preserving the order input by the user.
    # Formerly, we sorted() the kwds before looping.  The new way is *much*
    # faster; however, it means that f(x=1, y=2) will now be treated as a
    # distinct call from f(y=2, x=1) which will be cached separately.
    key = args
    if kwds:
        key += kwd_mark
        for item in kwds.items():
            key += item
    if typed:
        key += tuple(type(v) for v in args)
        if kwds:
            key += tuple(type(v) for v in kwds.values())
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)


class OutCacheWrapper:

    _logger = _logger

    def __init__(self):
        # cache: func_name --> self --> key(*inputs) --> value
        self._cache: Dict[str, Dict[object, Dict[Hashable, Any]]] = defaultdict(lambda: defaultdict(dict))
        # _influence_map: func_name --> influence_items
        self._influence_map: Dict[str, Tuple[Hashable, ...]] = {}
        # _fixed_map: self --> influence_item --> bool
        self._is_fixed_map: Dict[object, Dict[Hashable, bool]] = defaultdict(dict)

    def fixing(self, _self, influence_items: tuple = None):
        if influence_items is None:
            for k in self._is_fixed_map[_self]:
                _logger.debug(f'Set {_self} {k} Fixed')
                self._is_fixed_map[_self][k] = True
        else:
            for influence_item in influence_items:
                _logger.debug(f'Set {_self} {influence_item} Fixed')
                self._is_fixed_map[_self][influence_item] = True

    def _clean_cache(self, _self, influence_items: tuple = None):
        if influence_items is None:
            for func_name in self._cache:
                _logger.debug(f'Clean history cache of {_self}.{func_name}')
                self._cache[func_name][_self] = {}
        else:
            for func_name in self._cache:
                for _influence_item in self._influence_map[func_name]:
                    if _influence_item in influence_items:
                        _logger.debug(f'Clean history cache of {_self}.{func_name}')
                        self._cache[func_name][_self] = {}
                        break

    def modifying(self, _self, influence_items: tuple = None):
        self._clean_cache(_self, influence_items)
        if influence_items is None:
            for k in self._is_fixed_map[_self]:
                _logger.debug(f'Set {_self} {k} not Fixed')
                self._is_fixed_map[_self][k] = False
        else:
            for influence_item in influence_items:
                _logger.debug(f'Set {_self} {influence_item} not Fixed')
                self._is_fixed_map[_self][influence_item] = False

    def is_fixed(self, _self, influence_items: tuple = None) -> bool:
        return all(self._is_fixed_map[_self][influence_item] for influence_item in influence_items)

    def cache(self, *influence_items: Hashable, typed=False):
        def _wrapper_func(func):
            func_name = func.__name__
            self._cache[func_name] = {}
            self._influence_map[func_name] = influence_items

            # for influence_item in influence_items:
            #     self._is_fixed_map[influence_item] = False
            @functools.wraps(func)
            def _wrapped(_self, *args, **kwargs):
                _logger.debug(f'call wrapped {_self}.{func_name}({args}  kwargs: {kwargs})')

                if _self not in self._cache[func_name]:
                    # init the object
                    self._cache[func_name][_self] = {}
                    self._is_fixed_map[_self] = {}
                    for influence_item in influence_items:
                        self._is_fixed_map[_self][influence_item] = False

                _self_fixed_map = self._is_fixed_map[_self]
                if self.is_fixed(_self, influence_items):
                    # using cache
                    _logger.debug(f'{_self}.{func_name}({args}, {kwargs}) using cache.')
                    key = _make_key(args, kwargs, typed)
                    if key in self._cache[func_name][_self]:
                        return self._cache[func_name][_self][key]
                    _logger.debug(f'{_self}.{func_name}({args}, {kwargs}) updated cache.')
                    value = func(_self, *args, **kwargs)
                    self._cache[func_name][_self][key] = value
                    return value
                else:
                    # not using cache
                    _logger.debug(f'{_self}.{func_name}({args}, {kwargs}) NOT using cache.')
                    return func(_self, *args, **kwargs)

            return _wrapped
        return _wrapper_func


class OutCacheMixin:

    _cache_wrapper: OutCacheWrapper

    def fixing(self, influence_items: tuple = None):
        return self._cache_wrapper.fixing(self, influence_items)

    def modifying(self, influence_items: tuple = None):
        return self._cache_wrapper.modifying(self, influence_items)

    def is_fixed(self, influence_items: tuple = None):
        return self._cache_wrapper.is_fixed(self, influence_items)


if __name__ == '__main__':
    _logger.setLevel(logging.DEBUG)

    class TestClass(OutCacheMixin):

        _cache_wrapper = OutCacheWrapper()

        @_cache_wrapper.cache('default')
        def add(self, a, b):
            return a + b

    a = TestClass()
    a.add(1,2)
    a.fixing()


