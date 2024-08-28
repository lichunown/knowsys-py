import threading
import warnings
import inspect

from typing import *


def _checking_args(init_func):
    sig = inspect.signature(init_func)
    params = sig.parameters
    for param_name, param in list(params.items())[1:]:
        if param.default == sig.empty:
            raise AttributeError('When using `SingleInstance`, the function `__init__` need no extra inputs. '
                                 'try using `SingleEqualableInstance` or `SingleHashableInstance` instead.')


class SingleInstance(object):

    __instance__: Dict[str, Any]

    @classmethod
    @property
    def instance(cls):
        return cls.__instance__.get(cls.__name__)

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '__instance__', None):
            setattr(cls, '__instance__', dict())
        if cls.__name__ in cls.__instance__:
            return cls.__instance__[cls.__name__]

        res = super(SingleInstance, cls).__new__(cls)
        _checking_args(res.__init__)
        with threading.Lock():
            res.__init__(*args, **kwargs)
            cls.__instance__[cls.__name__] = res
        return cls.__instance__[cls.__name__]

    def __copy__(self):
        warnings.warn(f'You are trying to copy a single instance obj: `{self}`, '
                      f'which will only return itself.')
        return self

    def __deepcopy__(self, memodict={}):
        warnings.warn(f'You are trying to deepcopy a single instance obj: `{self}`, '
                      f'which will only return itself.')
        return self

