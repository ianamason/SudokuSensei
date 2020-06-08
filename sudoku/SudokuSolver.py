"""SudokuSolver is the interface with the Yices2 SMT solver."""

from yices import Census, Context, Model, Terms, Status, Yices

from .SudokuLib import Puzzle, Syntax, Cores

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

    def assert_puzzle_except(self, ctx, row, col, ans):
        assert ans == self.game.puzzle.get_cell(row, col)
        terms = []
        for i in range(9):
            for j in range(9):
                if i != row and j != col:
                    val = self.game.puzzle.get_cell(i, j)
                    if val is not None:
                        terms.append(self._equality(i, j, val))
        ctx.assert_formulas(terms)

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

    def filter_cores(self, solution, cutoff=5):
        cores = self.compute_cores(solution)
        if cores is None:
            return None
        #print('\nCores:\n')
        smallest = cores.least(cutoff)
        filtered = Cores(len(self.duplicate_rules))
        for core in smallest:
            ncore = self.filter_core(core)
            filtered.add(*ncore)
        #print('\nFiltered Cores:\n')
        smallest = filtered.least(5)
        return smallest

    def compute_cores(self, solution):
        cores = Cores(len(self.duplicate_rules))
        if solution is not None:
            for i in range(9):
                for j in range(9):
                    slot = self.game.puzzle.get_cell(i, j)
                    if slot is None:
                        ans = solution.get_cell(i, j)
                        core = self.compute_core(i, j, ans)
                        if core is None:
                            return None
                        cores.add(*core)
        return cores

    def compute_core(self, i, j, val):
        """We compute the unsat core of the duplicate_rules when asserting self.var(i, j) != val w.r.t the puzzle (val is assumed to be the unique solution)."""
        if not (0 <= i <= 8 and 0 <= j <= 8 and 1 <= val <= 9):
            raise Exception(f'Index error: {i} {j} {val}')
        context = Context()
        self.assert_puzzle(context)
        self.assert_not_value(context, i, j, val)
        self.assert_trivial_rules(context)
        smt_stat = context.check_context_with_assumptions(None, self.duplicate_rules)
        # a valid puzzle should have a unique solution, so this should not happen, if it does we bail
        if smt_stat != Status.UNSAT:
            #print(f'Error: {i} {j} {val} - not UNSAT: {Status.name(smt_stat)}')
            model = Model.from_context(context, 1)
            answer = self.puzzle_from_model(model)
            #print('Counter example (i.e. origonal puzzle does not have a unique solution):')
            answer.pprint()
            model.dispose()
            context.dispose()
            return None
        core = context.get_unsat_core()
        context.dispose()
        #print(f'Core: {i} {j} {val}   {len(core)} / {len(self.duplicate_rules)}')
        return (i, j, val, core)

    def filter_core(self, core):
        i, j, val, terms = core
        context = Context()
        self.assert_puzzle(context)
        self.assert_not_value(context, i, j, val)
        self.assert_trivial_rules(context)
        filtered = terms.copy()
        for term in terms:
            filtered.remove(term)
            smt_stat = context.check_context_with_assumptions(None, filtered)
            if smt_stat != Status.UNSAT:
                filtered.append(term)
        context.dispose()
        return (i, j, val, filtered)

    def erasable(self, ctx, i, j, val):
        """erasable returns True if puzzle (with [row, col] = val omitted) implies that [row, col] = val, it returns False otherwise.

        It is assumed that puzzle.get_cell(i,j) == val
        The context has already been informed of the rules.
        """
        ctx.push()
        self.assert_puzzle_except(ctx, i, j, val)
        self.assert_not_value(ctx, i, j, val)
        smt_stat = ctx.check_context(None)
        ctx.pop()
        return smt_stat == Status.UNSAT

    def get_hint(self):
        solution = self.solve()
        if solution is None:
            return (None, "There is no solution")
        cores = self.filter_cores(solution)
        if cores is None:
            return (None, "There must be a unique solution for a hint")
        i, j, val, terms = cores[0]
        return ((i, j, val, len(terms)), self.syntax.explain(terms))

    def show_hints(self, cores):
        for core in cores:
            i, j, val, terms = core
            print(f'[{i}, {j}] = {val} is forced by the following rules:')
            for term in terms:
                print(f'\t{self.syntax.explanation[term]}')
