"""SudokuSolver is the interface with the Yices2 SMT solver."""

from yices import Census, Context, Model, Terms, Status, Yices

from .SudokuLib import Puzzle, Syntax

from .Constants import ALEPH_NOUGHT


class SudokuSolver:

    """
    The Sudoku Solver, will solve when asked.

    iam: haven't really thought about the UI yet.


    """
    def __init__(self, game):
        self.game = game
        self.syntax = Syntax()
        # the matrix of uninterpreted terms
        self.variables = self.syntax.variables
        # the numerals as yices constants
        self.numerals = self.syntax.constants
        # each slot can only contain 1 through 9
        self.trivial_rules = self.syntax.trivial_rules
        # each row, column, and subsquare can not contain duplicates
        self.duplicate_rules = self.syntax.duplicate_rules
        # the union of the trivial rules and the duplicate rules
        self.all_rules = self.syntax.all_rules

    def dispose(self): # pylint: disable=R0201
        """dispose cleans up the solver's resources."""
        print(Census.dump())
        Yices.exit(True)

    def var(self, i, j):
        """var returns the variable at the specified cell."""
        return self.variables[i][j]

    def assert_rules(self, ctx):
        """assert_rules asserts the formulas the encode the Sudoku rules."""
        ctx.assert_formulas(self.all_rules)

    def assert_trivial_rules(self, ctx):
        """assert_trivial_rules asserts the fact that each variable must be in {1, 2, ..., 9}."""
        ctx.assert_formulas(self.trivial_rules)

    def assert_duplicate_rules(self, ctx):
        """asserts that each row, column and subsquare must not contain duplicates."""
        ctx.assert_formulas(self.duplicate_rules)

    def _equality(self, i, j, val):
        """the yices term asserting that cell [i, j] contains val."""
        return self.syntax.cell_equality(i, j, val)

    def _inequality(self, i, j, val):
        """the yices term asserting that cell [i, j] differs from val."""
        return self.syntax.cell_inequality(i, j, val)

    def assert_value(self, ctx, i, j, val):
        """asserts that cell [i, j] contains val."""
        if not (0 <= i <= 8 and 0 <= j <= 8 and 1 <= val <= 9):
            raise Exception(f'Index error: {i} {j} {val}')
        ctx.assert_formula(self._equality(i, j, val))

    def assert_not_value(self, ctx, i, j, val):
        """asserts that cell [i, j] is not val."""
        if not (0 <= i <= 8 and 0 <= j <= 8 and 1 <= val <= 9):
            raise Exception(f'Index error: {i} {j} {val}')
        ctx.assert_formula(self._inequality(i, j, val))

    def assert_puzzle(self, ctx):
        """Adds the diagram gleaned from the current state of the puzzle."""
        diagram = self.syntax.diagram(self.game.puzzle)
        ctx.assert_formulas(diagram)

    def solve(self):
        """Attempts to solve the puzzle, returning either None if there is no solution, or a board with the correct MISSING entries."""
        solution = None
        context = Context()
        self.assert_puzzle(context)
        self.assert_rules(context)
        smt_stat = context.check_context(None)
        if smt_stat != Status.SAT:
            print(f'No solution: smt_stat = {smt_stat}')
        else:
            #get the model
            model = Model.from_context(context, 1)
            #return the model as a board with ONLY the newly found values inserted.
            solution = self.puzzle_from_model(model, True)
            model.dispose()
        context.dispose()
        return solution

    def puzzle_from_model(self, model, only_new=False):
        """puzzle_from_model builds a puzzle from the given model.

        If the only_new argument is True, then only newly solved cells are included in returned the puzzle."""
        if model is None:
            return None
        puzzle = Puzzle()
        for i in range(9):
            for j in range(9):
                if only_new:
                    if self.game.puzzle.get_cell(i, j) is None:
                        puzzle.set_cell(i, j, model.get_value(self.var(i, j)))
                else:
                    puzzle.set_cell(i, j, model.get_value(self.var(i, j)))
        return puzzle

    #we could contrast the following with the  yices_assert_blocking_clause

    def count_models(self):
        """count_model returns the number of distinct solutions/models to the current problem."""
        def model2term(model):
            termlist = []
            for i in range(9):
                for j in range(9):
                    if self.game.puzzle.get_cell(i, j) is None:
                        val = model.get_value(self.variables[i][j])
                        var = self.variables[i][j]
                        value = self.numerals[val]
                        termlist.append(Terms.arith_eq_atom(var, value))
            return Terms.yand(termlist)
        result = 0
        context = Context()
        self.assert_puzzle(context)
        self.assert_rules(context)
        while  context.check_context(None) == Status.SAT:
            model = Model.from_context(context, 1)
            diagram = model2term(model)
            context.assert_formula(Terms.ynot(diagram))
            model.dispose()
            result += 1
            if result == ALEPH_NOUGHT:
                break
        context.dispose()
        return result
