import threading
import warnings
from typing import *


class SingleEqualableInstance(object):

    __instance__: Dict[str, List[Any]]

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '__instance__', None):
            setattr(cls, '__instance__', dict())
        res = super(SingleEqualableInstance, cls).__new__(cls)
        res.__init__(*args, **kwargs)

        if not getattr(res, '__eq__'):
            raise NotImplementedError('please implement the function `__eq__`.')

        with threading.Lock():
            if res.__class__.__name__ not in cls.__instance__:
                cls.__instance__[res.__class__.__name__] = []
            for ins in cls.__instance__[res.__class__.__name__]:
                if res == ins:
                    return ins
            cls.__instance__[res.__class__.__name__].append(res)
            return cls.__instance__[res.__class__.__name__][-1]

    def __copy__(self):
        warnings.warn(f'You are trying to copy a single instance obj: `{self}`, '
                      f'which will only return itself.')
        return self

    def __deepcopy__(self, memodict={}):
        warnings.warn(f'You are trying to deepcopy a single instance obj: `{self}`, '
                      f'which will only return itself.')
        return self

