"""SudokuGenerator contains a port of Daniel Beer's puzzle generation code (see ../generator/sugen.c)."""

import random

from .SudokuLib import SudokuError, Puzzle

from .SudokuOptions import Options

from .DB import solve_puzzle, generate_puzzle

_ELEMENTS = tuple(range(81))

_CELLS = tuple([(row, col) for row in range(9) for col in range(9)])

_BOOLS = (True, False)

def flip():
    """randomly chooses between True and False."""
    return random.choice(_BOOLS)

def random_cell():
    """randomly chooses a cell,"""
    return random.choice(_CELLS)

def random_index():
    """randomly chooses an index into the _CELLS tuple."""
    return random.choice(_ELEMENTS)

def index2cell(index):
    """get the cell corresponding to the given index."""
    if 0 <= index < 81:
        return _CELLS[index]
    raise SudokuError(f'index2cell error: {index}')

def pick_one(choices):
    """randomly chooses an element of the given set."""
    return random.choice(tuple(choices))

def _choose_b1(puzzle):
    """randomly fills the upper-left block with unique values from range(1, 10)."""
    choices = set(range(1, 10))
    for row in range(3):
        for col in range(3):
            val = pick_one(choices)
            choices.remove(val)
            puzzle.set_cell(row, col, val)

def _clear_b2(puzzle):
    for row in range(3):
        for col in range(3, 6):
            puzzle.erase_cell(row, col)

def _choose_b2(puzzle):
    """randomly fills the upper-center block with legal unique values from range(1, 10)."""
    for row in range(3):
        for col in range(3, 6):
            choices = puzzle.freedom_set(row, col)
            #print(f'[{row}, {col}]: {choices}')
            if len(choices) == 0:
                _clear_b2(puzzle)
                return False
            val = pick_one(choices)
            puzzle.set_cell(row, col, val)
    return True

def _clear_b3(puzzle):
    for row in range(3):
        for col in range(6, 9):
            puzzle.erase_cell(row, col)

def _choose_b3(puzzle):
    """randomly fills the upper-right block with legal unique values from range(1, 10)."""
    for row in range(3):
        for col in range(6, 9):
            choices = puzzle.freedom_set(row, col)
            if len(choices) == 0:
                _clear_b3(puzzle)
                return False
            val = pick_one(choices)
            puzzle.set_cell(row, col, val)
    return True

def _choose_c1(puzzle):
    """randomly fills in the rest of the first column."""
    col = 0
    for row in range(3, 9):
        choices = puzzle.freedom_set(row, col)
        val = pick_one(choices)
        puzzle.set_cell(row, col, val)


def _choose_rest(puzzle):
    least_free_cell = puzzle.freedom.least_free(puzzle.grid)
    if least_free_cell is None:
        return True
    row, col = least_free_cell

    choices = puzzle.freedom.freedom_set(*least_free_cell)

    while len(choices) > 0:
        val = pick_one(choices)
        choices.remove(val)
        puzzle.set_cell(row, col, val)

        if _choose_rest(puzzle):
            return True

    puzzle.erase_cell(row, col)
    return False

def choose_solution(puzzle):
    """choose_solution generates a random solution for an empty puzzle."""
    _choose_b1(puzzle)
    while True:
        if _choose_b2(puzzle):
            break
    while True:
        if _choose_b3(puzzle):
            break
    _choose_c1(puzzle)
    while True:
        if _choose_rest(puzzle):
            break
#    if not puzzle.sanity_check():
#        raise SudokuError('choose_solution: failed sanity check.')



class SolveContext:
    """SolveContext is the python analog to David Beer's solve_context struct."""
    def __init__(self, problem, solution):
        self.problem = problem.clone()
        self.count = 0
        self.solution = solution
        self.branch_score = 0


def _p_solve(problem, solution, diff, debug):
    """python equivalent to David Beer's solve function."""
    ctx = SolveContext(problem, solution)
    if not problem.sanity_check(debug):
        return -1
    _p_solve_recurse(ctx, 0)
    # calculate a difficulty score
    if diff is not None:
        diff[0] = (ctx.branch_score * 100) + problem.empty_cells
    if debug:
        print(f'solver returns {ctx.count - 1}  diff {diff[0] if diff is not None else "?"} empty {problem.empty_cells}')
    return ctx.count - 1


def _p_solve_recurse(ctx, diff):
    """python equivalent to David Beer's solve_recurse function (no sofa)."""
    least_free_cell = ctx.problem.least_free()
    if least_free_cell is None:
        if ctx.count == 0:
            ctx.branch_score = diff
            if ctx.solution is not None:
                ctx.solution.copy(ctx.problem)
        ctx.count += 1
        return
    row, col = least_free_cell
    free = ctx.problem.freedom.freedom_set(row, col)
    bf = len(free) - 1
    diff += bf * bf
    for val in free:
        ctx.problem.set_cell(row, col, val)
        _p_solve_recurse(ctx, diff)
        if ctx.count >= 2:
            return
    ctx.problem.erase_cell(row, col)


class SudokuGenerator:
    """The puzzle generation algorithm of Daniel Beer."""

    MAX_DIFF = -1

    def __init__(self, options=None):
        self.options = options if options is not None else Options()

    def solve(self, problem, solution, diff, sofa=None):
        """solve a puzzle according the user's options."""
        sofa = self.options.sofa if sofa is None else sofa
        if not self.options.use_c:
            return  _p_solve(problem, solution, diff, self.options.debug)
        return solve_puzzle(problem, solution, diff, sofa)


    def generate(self):
        """generate a puzzle, either using the python version of Daniel Beer's harden_puzzle, or the actual C."""
        if not self.options.use_c:
            return self._p_generate()
        return generate_puzzle(self.options.difficulty, self.options.sofa, -1, self.options.iterations)

    def _p_generate(self):
        """generate a puzzle, a version of Daniel Beer's harden_puzzle."""

        puzzle = Puzzle()
        choose_solution(puzzle)
        solution = puzzle.clone()

        if self.options.debug:
            puzzle.pprint()

        best = [0]
        code = _p_solve(puzzle, None, best, self.options.debug)

        if code != 0:
            print("Bug")
            return None

        for i in range(self.options.iterations):

            if self.options.debug:
                print(f'\tIteration: {i} {best[0]}')

            next_puzzle = puzzle.clone()

            for j in range(18):
                sx = [0]
                cx = random_index()
                r1, c1 = index2cell(cx)
                r2, c2 = index2cell(81 - cx - 1)

                if flip():
                    next_puzzle.set_cell(r1, c1, solution.get_cell(r1, c1))
                    next_puzzle.set_cell(r2, c2, solution.get_cell(r2, c2))
                else:
                    next_puzzle.erase_cell(r1, c1)
                    next_puzzle.erase_cell(r2, c2)

                code = _p_solve(next_puzzle, None, sx, self.options.debug)

                if code == 0:
                    if sx[0] > best[0]:
                        puzzle.copy(next_puzzle)
                    best[0] = sx[0]

                    if sx[0] >= self.options.difficulty:
                        if self.options.debug:
                            print(f'Iteration {i} {j}')
                        return (best[0], puzzle)


        if self.options.debug:
            print(f'Iteration {self.options.iterations}')
        return (best[0], puzzle)
