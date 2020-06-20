"""python bindings for Daniel Beer's Sudoku Generation library."""
import os
import sys

from ctypes import (
    c_bool,
    c_uint8,
    c_int32,
    c_uint32,
    CDLL,
    POINTER,
)

from ctypes.util import find_library

DEBUG = True

def sugen_library_name():
    """attempts to guess the name of the sugen library."""
    lib_basename = 'lib' + 'sugen'
    extension = '.so'
    if sys.platform == 'win32':
        extension = '.dll'
    elif sys.platform == 'cygwin':
        lib_basename = 'cyg' + 'sugen'
        extension = '.dll'
    elif sys.platform == 'darwin':
        extension = '.dylib'
    return f'{lib_basename}{extension}'

libsugenpath = find_library('sugen')

libsugen = None

if libsugenpath is None:
    libsugenpath = sugen_library_name()

def _loadSugenFromPath(path, library):
    global libsugen # pylint: disable=W0603
    try:
        where = os.path.join(path, library) if path is not None else library
        libsugen = CDLL(where)
        return True
    except Exception as exception: # pylint: disable=broad-except
        if DEBUG:
            sys.stderr.write(f'\nCDLL({where}) raised {exception}.\n')
        return False

def loadSugen():
    """attempts to load the sugen library, relying on CDLL, and using /usr/local/lib as a backup plan."""
    global libsugenpath # pylint: disable=W0603
    global libsugen # pylint: disable=W0603
    error_msg = "Sugen dynamic library not found."
    if _loadSugenFromPath(None, libsugenpath):
        return
    if _loadSugenFromPath('/usr/local/lib', libsugenpath):
        return
    if _loadSugenFromPath('./generator', libsugenpath):
        return
    # else we failed
    raise Exception(error_msg)

loadSugen()

def make_puzzle_array(pyarray):
    """Makes a C term array object from a python array object"""
    assert len(pyarray) == 81
    retval = None
    if pyarray is not None:
        #weird python and ctype magic
        retval = (c_uint8 * len(pyarray))(*pyarray)
    return retval

def make_uint32_array(pyarray):
    """Makes a C uint32 array object from a python array object"""
    retval = None
    if pyarray is not None:
        #weird python and ctype magic
        retval = (c_uint32 * len(pyarray))(*pyarray)
    return retval


#void db_generate_puzzle(uint8_t* puzzle, uint32_t* difficultyp, uint32_t difficulty, uint32_t max_difficulty, uint32_t iterations, bool sofa);


#int32_t db_solve_puzzle(uint8_t* puzzle, uint8_t* solution, uint32_t* difficultyp, bool sofa);
libsugen.db_solve_puzzle.restype = c_int32
libsugen.db_solve_puzzle.argtypes = [POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint32), c_bool]
def solve_puzzle(puzzle, solution, difficultyp, sofa):
    """call's daniel beer's puzzle solver, both solution and difficultyp can be NULL."""
    cpuzzle = make_puzzle_array(puzzle)
    csolution = make_puzzle_array(solution) if solution is not None else None
    assert len(difficultyp) == 1
    cdifficultyp = make_uint32_array(difficultyp)
    return libsugen.db_solve_puzzle(cpuzzle, csolution, cdifficultyp, sofa)
