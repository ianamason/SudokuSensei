"""SudokuSolver is the interface with the Yices2 SMT solver."""

from yices import Context, Model, Terms, Status, Yices

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
        # the context (a set/stack of yices assertions)
        self.context = Context()
        # add the rules of the game
        self.assert_rules()


    def dispose(self):
        """dispose cleans up the solver's resources."""
        self.context.dispose()
        Yices.exit(True)


    def var(self, i, j):
        """var returns the variable at the specified cell."""
        return self.variables[i][j]

    def assert_rules(self):
        """assert_rules asserts the formulas the encode the Sudoku rules."""
        self.context.assert_formulas(self.syntax.trivial_rules)
        self.context.assert_formulas(self.syntax.duplicate_rules)

    def assert_diagram(self):
        """Adds the diagram gleaned from the current state of the puzzle."""
        diagram = self.syntax.diagram(self.game.puzzle)
        self.context.assert_formulas(diagram)

    def solve(self):

        """Attempts to solve the puzzle, returning either None if there is no solution, or a board with the correct MISSING entries."""
        solution = None

        #we use push and pop so that we can solve (variants) repeatedly without having to start from scratch each time.
        self.context.push()

        self.assert_diagram()

        smt_stat = self.context.check_context(None)

        if smt_stat != Status.SAT:
            print(f'No solution: smt_stat = {smt_stat}')
        else:
            #get the model
            model = Model.from_context(self.context, 1)
            #return the model as a board with ONLY the newly found values inserted.
            solution = self.puzzle_from_model(model, True)
            model.dispose()

        self.context.pop()
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
        self.context.push()
        self.assert_diagram()
        while  self.context.check_context(None) == Status.SAT:
            model = Model.from_context(self.context, 1)
            diagram = model2term(model)
            self.context.assert_formula(Terms.ynot(diagram))
            model.dispose()
            result += 1
            if result == ALEPH_NOUGHT:
                break
        self.context.pop()
        return result
