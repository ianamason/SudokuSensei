"""SudokuGenerator contains a port of Daniel Beer's puzzle generation code (see ../generator/sugen.c)."""

import random

def _choose_b1(puzzle):
    """randomly fills the upper-left subsquare with unique values from range(1, 10)."""
    choices = set(range(1, 10))
    for row in range(3):
        for col in range(3):
            val = random.choice(tuple(choices))
            choices.remove(val)
            puzzle.set_cell(row, col, val)

def _clear_b2(puzzle):
    for row in range(3):
        for col in range(3, 6):
            puzzle.erase_cell(row, col)

def _choose_b2(puzzle):
    """randomly fills the upper-center subsquare with legal unique values from range(1, 10)."""
    for row in range(3):
        for col in range(3, 6):
            choices = puzzle.freedom_set(row, col)
            if len(choices) == 0:
                _clear_b2(puzzle)
                return False
            val = random.choice(tuple(choices))
            puzzle.set_cell(row, col, val)
    return True

def _clear_b3(puzzle):
    for row in range(3):
        for col in range(6, 9):
            puzzle.erase_cell(row, col)

def _choose_b3(puzzle):
    """randomly fills the upper-right subsquare with legal unique values from range(1, 10)."""
    for row in range(3):
        for col in range(6, 9):
            choices = puzzle.freedom_set(row, col)
            if len(choices) == 0:
                _clear_b3(puzzle)
                return False
            val = random.choice(tuple(choices))
            puzzle.set_cell(row, col, val)
    return True

def _choose_c1(puzzle):
    col = 0
    for row in range(9):
        choices = puzzle.freedom_set(row, col)
        val = random.choice(tuple(choices))
        puzzle.set_cell(row, col, val)


def _choose_rest(puzzle):
    least_free_cell = puzzle.freedom.least_free(puzzle.grid)
    if least_free_cell is None:
        return True
    row, col = least_free_cell

    choices = puzzle.freedom.freedom_set(*least_free_cell)

    while len(choices) > 0:
        val = random.choice(tuple(choices))
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
    _choose_rest(puzzle)



class SolveContext:
    """SolveContext is the python analog to David Beer's solve_context struct."""
    def __init__(self, problem, solution):
        self.problem = problem.clone()
        self.count = 0
        self.solution = solution
        self.branch_score = 0


def solve(problem, solution, diff):
    """python equivalent to David Beer's solve function."""
    ctx = SolveContext(problem, solution)

    solve_recurse(ctx, problem.freedom, 0)

    # calculate a difficulty score
    if diff is not None:
        empty = problem.empty_cells
        # why not just have a puzzle maintain it's own empty count?
        #for row in range(9):
        #    for col in range(9):
        #        if problem.get_cell(row, col) is None:
        #            empty += 1
        #assert empty == problem.empty_cells

        diff[0] = (ctx.branch_score * 100) + empty


    return ctx.count - 1


def solve_recurse(ctx, freedom, diff):
    """python equivalent to David Beer's solve_recurse function."""

    least_free_cell = freedom.least_free(ctx.problem.grid)

    if least_free_cell is None:
        if ctx.count == 0:
            ctx.branch_score = diff
            ctx.solution.copy(ctx.problem)
            ctx.count += 1
        return

    row, col = least_free_cell

    free = freedom.freedom_set(row, col)
    bf = len(free) - 1
    diff += bf * bf

    for val in free:
        new_freedom = freedom.clone()  #FIXME: I don't think cloning is necessary
        new_freedom.constrain_set_cell(row, col, val, None)
        ctx.problem.set_cell(row, col, val)
        solve_recurse(ctx, new_freedom, diff)
        if ctx.count >= 2:
            return

    ctx.problem.erase_cell(row, col)
