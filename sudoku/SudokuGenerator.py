"""SudokuGenerator contains a port of Daniel Beer's puzzle generation code (see ../generator/sugen.c)."""



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
        empty = 0
        # why not just have a puzzle maintain it's own empty count?
        for row in range(9):
            for col in range(9):
                if problem.get_cell(row, col) is None:
                    empty += 1
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
        new_freedom = freedom.clone()
        new_freedom.constrain_set_cell(row, col, val, None)
        ctx.problem.set_cell(row, col, val)
        solve_recurse(ctx, new_freedom, diff)
        if ctx.count >= 2:
            return

    ctx.problem.erase_cell(row, col)
