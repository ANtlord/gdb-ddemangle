import shutil
from subprocess import Popen, PIPE, STDOUT
from gdb import Frame
from gdb import frame_filters
from gdb.FrameDecorator import FrameDecorator
from typing import Iterator


EXECUTABLE = 'ddemangle'
YELLOW = '\x1b[33m'
END = '\x1b[0m'
HELP_MESSAGE = ('ddemangle is not installed or it\'s not available at ' +
                '$PATH variable. Try exectue `which ddemangle`')
HEADS = '_D4', '_D3'


def is_mangled_d_symbol(symbol: str) -> bool:
    return any(symbol.startswith(x) for x in HEADS)


class DemangleController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._start_application()
        return cls._instance

    def _start_application(self):
        self._pipe = Popen(
            EXECUTABLE, stdout=PIPE, stdin=PIPE, stderr=STDOUT,
            universal_newlines=True
        )

    def demangle(self, data: str) -> str:
        try:
            print(data.encode(), file=self._pipe.stdin, flush=True)
        except BrokenPipeError:
            self._start_application()
            print(data.encode(), file=self._pipe.stdin, flush=True)
        return self._pipe.stdout.readline()[2:-2]


class DdemangleFilter:
    """
    Helps to demangle traceback debugging an application that is written in D.
    """
    def __init__(self, name='ddemangle-filter', priority=0, enabled=True):
        self.name = name
        self.priority = priority
        if shutil.which(EXECUTABLE):
            self.enabled = enabled
        else:
            self.enabled = False
            print("%s%s%s" % (YELLOW, HELP_MESSAGE, END))
            return
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
        self.demangleController = DemangleController()

    def function(self):
        """Changes function name using Ddemangle if it starts with _D4, _D3"""
        function_symbol = super().function()
        if isinstance(function_symbol, int):
            try:
                function_symbol = try_get_function_name(function_symbol)
            except NotMangledSymbol:
                return function_symbol

        if is_mangled_d_symbol(function_symbol):
            function_symbol = self.demangleController.demangle(function_symbol)
        return function_symbol


DdemangleFilter()
