# GDB Ddemangle

Helps to demangle traceback debugging an application that is written in D.

## Requirements

* Python 3.5 or above ([How to check](#check-python-version))
* Installed [ddemangle](https://github.com/dlang/tools/blob/master/ddemangle.d) avaialable at PATH variable

## Installation

* `mkdir ~/.gdb/ && cd ~/.gdb`
* `git clone https://github.com/ANtlord/gdb-ddemangle`
* `cd gdb-ddemangle && make` in order to create binary that demangles D symbols
* Create a file `.gdbinit` if it doesn't exist yet
* Add `source .gdb/gdb-ddemangle/ddemangle.py`. If you use
  [gdb-colour-filter](https://github.com/daskol/gdb-colour-filter) add the line
  above `source .gdb/gdb-colour-filter/colour_filter.py`

## Check Python version

* Run `gdb`
* Run `python print(sys.version)` in GDB

## Result

### Before

![Before](before.png)

### After

![After](after.png)
