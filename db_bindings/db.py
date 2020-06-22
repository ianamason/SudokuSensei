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
from sudoku.SudokuLib import SudokuError, Puzzle, puzzle2pyarray, pyarray2puzzle
from sudoku.Constants import DEBUG

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
    if _loadSugenFromPath('./generator', libsugenpath):
        return True
    if _loadSugenFromPath(None, libsugenpath):
        return True
    if _loadSugenFromPath('/usr/local/lib', libsugenpath):
        return True
    return False


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


success = loadSugen()
if not success:
    raise SudokuError("Sugen dynamic library not found.")

#void db_generate_puzzle(uint8_t* puzzle, uint32_t* difficultyp, uint32_t difficulty, uint32_t max_difficulty, uint32_t iterations, bool sofa);


#int32_t db_solve_puzzle(uint8_t* puzzle, uint8_t* solution, uint32_t* difficultyp, bool sofa);
libsugen.db_solve_puzzle.restype = c_int32
libsugen.db_solve_puzzle.argtypes = [POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint32), c_bool]
def solve_puzzle(puzzle, solution, difficultyp, sofa):
    """call's daniel beer's puzzle solver, both solution and difficultyp can be NULL."""
    assert len(puzzle) == 81
    assert solution is None or len(solution) == 81
    assert difficultyp is None or len(difficultyp) == 1
    cpuzzle = make_puzzle_array(puzzle)
    csolution = make_puzzle_array(solution) if solution is not None else None
    cdifficultyp = make_uint32_array(difficultyp) if difficultyp is not None else None
    retval = libsugen.db_solve_puzzle(cpuzzle, csolution, cdifficultyp, sofa)
    if difficultyp is not None:
        difficultyp[0] = cdifficultyp[0]
    if retval == 0 and solution is not None:
        for cell in range(81):
            solution[cell] = csolution[cell]
    return retval


def main():
    """test harness for the bindings."""
    puzzle = Puzzle.resource2puzzle('extreme3')
    solution = Puzzle()
    puzzle.pprint()
    pypuz = puzzle2pyarray(puzzle)
    pysol = puzzle2pyarray(solution)
    diff = [0]
    retval = solve_puzzle(pypuz, pysol, diff, False)
    if retval == 0:
        csol = pyarray2puzzle(pysol)
        solution.copy(csol)
    print(f'Difficulty = {diff[0]}')
    solution.pprint()

if __name__ == '__main__':
    main()
