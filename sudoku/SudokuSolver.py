"""SudokuSolver is the interface with the Yices2 SMT solver."""

from yices import Context, Model, Terms, Types, Status, Yices

from .SudokuLib import Puzzle, make_grid

from .Constants import ALEPH_NOUGHT


class SudokuSolver:

    """
    The Sudoku Solver, will solve when asked.

    iam: haven't really thought about the UI yet.


    """
    def __init__(self, game):
        self.game = game
        # the matrix of uninterpreted terms
        self.variables = self.__create_variables()
        # the numerals as yices constants
        self.numerals = self.__create_numerals()
        # the context (a set/stack of yices assertions)
        self.context = Context()
        # add the generic constraints (corresponding to the rules of the game)
        self.__generate_constraints()


    def dispose(self):
        """dispose cleans up the solver's resources."""
        self.context.dispose()
        Yices.exit(True)


    def var(self, i, j):
        """var returns the variable at the specified cell."""
        return self.variables[i][j]

    def __create_variables(self): # pylint: disable=R0201
        """Creates the matrix of uninterpreted terms that represents the logical view of the board."""
        int_t = Types.int_type()
        variables = make_grid()
        for i in range(9):
            for j in range(9):
                variables[i][j] = Terms.new_uninterpreted_term(int_t)
        return variables

    def __create_numerals(self): # pylint: disable=R0201
        """Creates a mapping from digits to yices constants for those digits."""
        numerals = {}
        for i in range(1, 10):
            numerals[i] = Terms.integer(i)
        return numerals


    def __generate_constraints(self): # pylint: disable=R0201
        # each x is between 1 and 9
        def between_1_and_9(x):
            return Terms.yor([Terms.eq(x, self.numerals[i+1]) for i in range(9)])
        for i in range(9):
            for j in range(9):
                self.context.assert_formula(between_1_and_9(self.variables[i][j]))

        # All elements in a row must be distinct
        for i in range(9):
            self.context.assert_formula(Terms.distinct([self.variables[i][j] for j in range(9)]))


        # All elements in a column must be distinct
        for i in range(9):
            self.context.assert_formula(Terms.distinct([self.variables[j][i] for j in range(9)]))

        # All elements in each 3x3 square must be distinct
        for row in range(3):
            for column in range(3):
                self.context.assert_formula(Terms.distinct([self.variables[i + 3 * row][j + 3 * column] for i in range(3) for j in range(3)]))


    def __add_facts(self):
        """Adds the facts gleaned from the current state of the puzzle."""
        def set_value(row, column, value):
            assert 0 <= row < 9
            assert 0 <= column < 9
            assert 1 <= value <= 9
            self.context.assert_formula(Terms.arith_eq_atom(self.variables[row][column], self.numerals[value]))


        for i in range(9):
            for j in range(9):
                value = self.game.puzzle.get_cell(i, j)
                if value is not None:
                    set_value(i, j, value)

    def solve(self):

        """Attempts to solve the puzzle, returning either None if there is no solution, or a board with the correct MISSING entries."""
        solution = None

        #we use push and pop so that we can solve (variants) repeatedly without having to start from scratch each time.
        self.context.push()

        self.__add_facts()

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
        self.__add_facts()
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
