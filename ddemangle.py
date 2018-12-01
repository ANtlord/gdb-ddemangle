import ctypes
import os
import shutil
from subprocess import Popen, PIPE, STDOUT
from typing import Iterator
from gdb import Frame
from gdb import frame_filters
from gdb.FrameDecorator import FrameDecorator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(BASE_DIR, 'lib.so')

if not os.path.exists(LIB):
    print("Can't find %s. Run make inside %s" % (LIB, BASE_DIR))
    exit(1)

module = ctypes.cdll.LoadLibrary(LIB)
module.dem.restype = ctypes.c_char_p
module.dem.argtypes = [ctypes.c_char_p]

class DdemangleController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def demangle(self, data: str) -> str:
        return module.dem(data)


class DdemangleFilter:
    """
    Helps to demangle traceback debugging an application that is written in D.
    """
    def __init__(self, name='ddemangle-filter', priority=0, enabled=True):
        self.name = name
        self.priority = priority
        self.enabled = enabled
        frame_filters[self.name] = self

    def filter(self, iters: Iterator[Frame]) -> Iterator[Frame]:
        return (DdemangleFrameDecorator(x) for x in iters)


class NotMangledSymbol(Exception):
    pass


def try_get_function_name(with_address: int) -> str:
    symbol = gdb.execute('info symbol 0x%016x' % with_address, False, True)
    flag = any(symbol.startswith(x) for x in HEADS)
    if is_mangled_d_symbol(symbol):
        return symbol.split()[0]
    raise NotMangledSymbol


class DdemangleFrameDecorator(FrameDecorator):
    def __init__(self, fobj: Frame):
        super().__init__(fobj)
        self.demangleController = DdemangleController()

    def function(self):
        """Changes function name using Ddemangle if it starts with _D4, _D3"""
        function_symbol = super().function()
        if isinstance(function_symbol, int):
            try:
                function_symbol = try_get_function_name(function_symbol)
            except NotMangledSymbol:
                return function_symbol

        function_symbol = module.dem(function_symbol.encode())
        return function_symbol.decode()


DdemangleFilter()
