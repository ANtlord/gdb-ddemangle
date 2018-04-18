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
            print(f'{YELLOW}{HELP_MESSAGE}{END}')
            return
        frame_filters[self.name] = self
        self.pipe = Popen(
            EXECUTABLE, stdout=PIPE, stdin=PIPE, stderr=STDOUT
        )

    def filter(self, iters: Iterator[Frame]) -> Iterator[Frame]:
        return (DdemangleFrameDecorator(x, self.pipe) for x in iters)


class DdemangleFrameDecorator(FrameDecorator):
    def __init__(self, fobj: Frame, pipe):
        super().__init__(fobj)
        self.pipe = pipe

    def function(self):
        """Changes function name using Ddemangle if it starts with _D4"""
        res = super().function()

        if res.startswith('_D4'):
            res = self.pipe.communicate(input=res.encode())[0].decode()[:-1]
        return res


DdemangleFilter()
