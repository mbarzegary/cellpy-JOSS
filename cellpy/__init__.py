# -*- coding: utf-8 -*-

"""

"""

__author__ = (
    "Jan Petter Maehlen",
    "Asbjoern Ulvestad",
    "Muhammad Abdelhamid",
    "Julia Wind",
)
__email__ = (
    "jepe@ife.no",
    "Asbjorn.Ulvestad@ife.no",
    "Muhammad.Abdelhamid@ife.no",
    "julia.wind@ife.no",
)

import logging
import warnings

import cellpy._version
from cellpy.parameters import prms  # TODO: this might give circular ref
from cellpy.parameters import prmreader
from cellpy.readers import cellreader, dbreader, filefinder, do
from cellpy.readers.core import Q, ureg

__version__ = cellpy._version.__version__

logging.getLogger(__name__).addHandler(logging.NullHandler())

# TODO: (v2.0) remove this and enforce using for example `import cellpy.session as clp` and then
#  run `prmreader.initialize` in that `__init__` instead:
init = prmreader.initialize
init()

# TODO: (v2.0) remove this and enforce using `cellpy.get` (or `cellpy.cellreader.get`) instead:
get = cellreader.get

__all__ = [
    "cellreader",
    "dbreader",
    "prmreader",
    "prms",
    "filefinder",
    "get",
    "do",
    "init",
    "ureg",
    "Q",
]
