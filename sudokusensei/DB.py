"""python bindings for Daniel Beer's Sudoku Generation library."""
import os
import os.path
import sys

from ctypes import (
    c_bool,
    c_uint8,
    c_int32,
    c_uint32,
    CDLL,
    POINTER,
)

from pkg_resources import resource_filename


from .SudokuLib import SudokuError, Puzzle, make_grid

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

libsugen = sugen_library_name()

libsugenpath = resource_filename('sudokusensei', 'lib/libsugen.dylib')

if not os.path.exists(libsugenpath):
    raise SudokuError(f'The necessary shared library {libsugenpath} does not exist.')

libsugen = CDLL(libsugenpath)

if libsugen is None:
    raise SudokuError(f'The necessary shared library {libsugenpath} did not load.')

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

def puzzle2pyarray(puzzle):
    """flattens a puzzle to an array of length 81."""
    retval = [0] * 81
    matrix = puzzle.grid
    for row in range(9):
        for col in range(9):
            val = matrix[row][col]
            if val is not None:
                retval[9 * row + col] = val
    return retval

def pyarray2puzzle(pyarray):
    """creates a puzzle from pyarray of length 81."""
    assert (len(pyarray)) == 81
    matrix = make_grid()
    for row in range(9):
        for col in range(9):
            val = pyarray[9 * row + col]
            if val != 0:
                matrix[row][col] = val
    return Puzzle(matrix)


#void db_debug(bool dbg);
libsugen.db_debug.argtypes = [c_bool]
def db_debug(dbg):
    """switches on/off 'informative' print statments."""
    libsugen.db_debug(dbg)

#void db_generate_puzzle(uint8_t* puzzle, uint32_t* difficultyp, uint32_t target_difficulty, uint32_t max_difficulty, uint32_t iterations, bool sofa);
libsugen.db_generate_puzzle.argtypes = [POINTER(c_uint8), POINTER(c_uint32), c_uint32, c_uint32, c_uint32, c_bool]
def db_generate_puzzle(puzzle, difficultyp, target_difficulty, max_difficulty, iterations, sofa):
    """call's daniel beer's puzzle generator."""
    assert len(puzzle) == 81
    assert len(difficultyp) == 1
    cpuzzle = make_puzzle_array(puzzle)
    cdifficultyp = make_uint32_array(difficultyp) if difficultyp is not None else None
    libsugen.db_generate_puzzle(cpuzzle, cdifficultyp, target_difficulty, max_difficulty, iterations, sofa)
    difficultyp[0] = cdifficultyp[0]
    for cell in range(81):
        puzzle[cell] = cpuzzle[cell]

#int32_t db_solve_puzzle(uint8_t* puzzle, uint8_t* solution, uint32_t* difficultyp, bool sofa);
libsugen.db_solve_puzzle.restype = c_int32
libsugen.db_solve_puzzle.argtypes = [POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint32), c_bool]
def db_solve_puzzle(puzzle, solution, difficultyp, sofa):
    """call's daniel beer's puzzle solver, both solution and difficultyp can be NULL."""
    # explain the arguments
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

def solve_puzzle(puzzle, solution, diff, sofa):
    """SudokuSensei interface to Daniel Beer's solver."""
    pypuz = puzzle2pyarray(puzzle)
    pysol = puzzle2pyarray(solution) if solution is not None else None
    difficulty = [0]
    retval = db_solve_puzzle(pypuz, pysol, difficulty, sofa)
    if retval == 0:
        if solution is not None:
            csol = pyarray2puzzle(pysol)
            solution.copy(csol)
        if diff is not None:
            diff[0] = difficulty[0]
    return retval

def generate_puzzle(target, sofa=False, max_difficulty=-1, iterations=200):
    """SudokuSensei interface to Daniel Beer's generator."""
    pypuz = [0] * 81
    diff = [0]
    db_generate_puzzle(pypuz, diff, target, max_difficulty, iterations, sofa)
    puzzle = pyarray2puzzle(pypuz)
    return (diff[0], puzzle)

def test_solve():
    """test the solver."""
    puzzle = Puzzle.resource2puzzle('extreme3')
    solution = Puzzle()
    puzzle.pprint()
    pypuz = puzzle2pyarray(puzzle)
    pysol = puzzle2pyarray(solution)
    diff = [0]
    retval = db_solve_puzzle(pypuz, pysol, diff, True)
    if retval == 0:
        csol = pyarray2puzzle(pysol)
        solution.copy(csol)
    print(f'Difficulty = {diff[0]}')
    solution.pprint()

def test_generate(target, iterations, sofa):
    """test the generator."""
    pypuz = [0] * 81
    diff = [0]
    db_generate_puzzle(pypuz, diff, target, -1, iterations, sofa)
    puzzle = pyarray2puzzle(pypuz)
    puzzle.pprint()
    print(f'Difficulty = {diff[0]} Empty cells: {puzzle.empty_cells}')



def main():
    """test the bindings."""
    if True: # pylint: disable=W0125
        test_generate(700, 10000, True)
    else:
        test_solve()
        for _ in range(100):
            sofa_difficulty, puzzle = generate_puzzle(700, True, iterations=1000)
            no_sofa_difficulty = [0]
            retval = solve_puzzle(puzzle, None, no_sofa_difficulty, False)
            assert retval == 0
            if sofa_difficulty > no_sofa_difficulty[0]:
                print('Counterexample:')
                puzzle.pprint()
            print(f'no sofa: {no_sofa_difficulty[0]}  sofa: {sofa_difficulty} empty cells:  {puzzle.empty_cells}')

if __name__ == '__main__':
    main()
