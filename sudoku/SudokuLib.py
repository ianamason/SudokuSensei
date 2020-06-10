"""A library to store useful routines and keep the clutter to a minimum."""

import argparse


from yices.Types import Types
from yices.Terms import Terms

from .StringBuilder import StringBuilder

int_t = Types.int_type()

def parse_arguments():
    """
    Parses arguments of the form:
        sudokusolver --board <board name>
    Where `board name` must be in the `BOARD` list
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--board',
                            help='Desired board name',
                            type=str,
                            required=False)

    # Creates a dictionary of keys = argument flag, and value = argument
    args = vars(arg_parser.parse_args())
    return args['board']





def make_grid():
    """make_grid constructs a 9x9 grid all whose entries are initially None."""
    grid = [None] * 9
    for i in range(9):
        grid[i] = [None] * 9
    return grid

def make_constants():
    """make_constants makes a map from the digits 1 through 9 to the Yices constant denoting that digit."""
    constants = {}
    for i in range(1, 10):
        constants[i] = Terms.integer(i)
    return constants

def make_variables():
    """make_variables creates a 9x9 grid with each cell containing the Yices term representing that cell."""
    variables = make_grid()
    for i in range(9):
        for j in range(9):
            variables[i][j] = Terms.new_uninterpreted_term(int_t)
    return variables

def make_freedom_map():
    """constructs an initially empty freedom map."""
    freedom = {}
    for row in range(9):
        for col in range(9):
            # the set represents the values a cell CANNOT take
            freedom[(row, col)] = set()
    return freedom

class SudokuError(Exception):
    """An application specific error."""


class Freedom:
    """Represents simple freedom analysis of a puzzle.

    Each cell is assigned the set of values that it can legally take (irregardless of
    whether they contain a value already). The map is updated as the puzzle is mutated.
    """

    def __init__(self):
        self.freedom = make_freedom_map()

    def _clear_map(self):
        """resets the map"""
        for row in range(9):
            for col in range(9):
                self.freedom[(row, col)].clear()

    def _constrain_row(self, row, col, val, erase=False):
        for cx in range(9):
            if cx != col:
                sx = self.freedom[(row, cx)]
                if erase:
                    sx.discard(val)
                else:
                    sx.add(val)

    def _constrain_col(self, row, col, val, erase=False):
        for rx in range(9):
            if rx != row:
                sx = self.freedom[(rx, col)]
                if erase:
                    sx.discard(val)
                else:
                    sx.add(val)

    def _constrain_subsquare(self, row, col, val, erase=False):
        for rs, cs in Puzzle.subsquare(row, col):
            if (rs, cs) != (row, col):
                sx = self.freedom[(rs, cs)]
                if erase:
                    sx.discard(val)
                else:
                    sx.add(val)

    def constrain_set_cell(self, row, col, val, oval):
        """update the freedom map by adding the fact that cell (row, col) contents is being updated from oval to val."""
        if oval is not None:
            self.constrain_erase_cell(row, col, oval)
        self._constrain_row(row, col, val)
        self._constrain_col(row, col, val)
        self._constrain_subsquare(row, col, val)


    def constrain_erase_cell(self, row, col, oval):
        """update the freedom map by removing the fact that cell (row, col) contains oval."""
        self._constrain_row(row, col, oval, True)
        self._constrain_col(row, col, oval, True)
        self._constrain_subsquare(row, col, oval, True)


    def constrain(self, matrix):
        """computes the set oriented freedom analysis."""
        for row in range(9):
            for col in range(9):
                val = matrix[row][col]
                if val is not None:
                    # val cannot be in any the cell in this row
                    self._constrain_row(row, col, val)
                    # val cannot be in any the cell in this column
                    self._constrain_col(row, col, val)
                    # val cannot be in any the cell in this subsquare
                    self._constrain_subsquare(row, col, val)


    def freedom_set(self, row, col):
        """returns the set of possible (immediate) choices for the given cell.

        I.e. the complement of the set we store in the map for rthe given cell.
        """
        sx = self.freedom[(row, col)]
        return set(range(1, 10)).difference(sx)

    def least_free(self, matrix):
        """least_free returns the empty cell with the least freedom."""
        least = None
        least_size = 0
        for row in range(9):
            for col in range(9):
                if matrix[row][col] is None:
                    sx = self.freedom[(row, col)]
                    sxz = len(sx)
                    if  sxz > least_size:
                        least = (row, col)
                        least_size = sxz
        return least

    def clone(self):
        """return an exact copy that shares no structure."""
        copy = Freedom()
        for row in range(9):
            for col in range(9):
                copy.freedom[(row, col)].update(self.freedom[(row, col)])
        return copy


class Puzzle:
    """Puzzle is a 9x9 grid of digits between 1 and 9 inclusive, or None."""

    def puzzle2path(self, path):
        """puzzle2path writes the puzzle out the the file specified by 'path'."""
        with open(path, 'w') as fp:
            fp.write(self.to_string('', '0'))

    @staticmethod
    def path2puzzle(path):
        """path2puzzle reads, parses and creates a puzzle from the given 'path'."""
        with open(path, 'r') as fp:
            matrix = make_grid()
            row = 0
            col = 0
            for line in fp:
                line = line.strip()
                if len(line) != 9:
                    raise SudokuError('Each line in the sudoku puzzle must be 9 chars long.')
                for char in line:
                    if not char.isdigit():
                        raise SudokuError('Valid characters for a sudoku puzzle must be in 0-9')
                    digit = int(char)
                    if digit != 0:
                        matrix[row][col] = digit # pylint: disable=E1137
                    col += 1
                row += 1
                col = 0
                if row == 9:
                    break
            return Puzzle(matrix)

    @staticmethod
    def subsquare(orow, ocol):
        """returns a list of cells that make up the subsquare the cell belongs to."""
        if 0 <= orow <= 8 and 0 <= ocol <= 8:
            row = 3 * (orow // 3)
            col = 3 * (ocol // 3)

            return [(r, c) for r in range(row, row + 3) for c in range(col, col + 3)]
        raise SudokuError(f'subsquare error: {orow} {ocol}')


    def __init__(self, matrix=None):
        self.grid = make_grid()
        self.freedom = Freedom()
        if matrix is not None:
            for i in range(9):
                for j in range(9):
                    val = matrix[i][j]
                    if val is not None:
                        self.set_cell(i, j, val)

    def copy(self, puzzle):
        """copy the state of another puzzle."""
        self.__init__(puzzle.grid)

    def agree(self, puzzle):
        """see if two puzzles agree on non-None cells."""
        for row in range(9):
            for col in range(9):
                mine = self.get_cell(row, col)
                theirs = puzzle.get_cell(row, col)
                if mine is not None and theirs is not None:
                    if mine != theirs:
                        return False
        return True


    def get_row(self, row):
        """get_row returns a copy of the given row."""
        if 0 <= row <= 8:
            return self.grid[row].copy()
        raise SudokuError(f'get_row error: {row}')


    def clone(self):
        """clone creates a deep copy of the puzzle."""
        matrix = [self.get_row(row) for row in range(9)]
        return Puzzle(matrix)

    def erase_cell(self, i, j):
        """erase_cell erases the contents of the cell in the puzzle."""
        if 0 <= i <= 8 and 0 <= j <= 8:
            val = self.grid[i][j]
            if val is not None:
                self.grid[i][j] = None
                self.freedom.constrain_erase_cell(i, j, val)
            return None
        raise SudokuError(f'erase_cell error: {i} {j}')

    def set_cell(self, i, j, val):
        """set_cell set the value of the given cell to the provided value."""
        if 0 <= i <= 8 and 0 <= j <= 8 and 1 <= val <= 9:
            oval = self.grid[i][j]
            if oval != val:
                self.grid[i][j] = val
                self.freedom.constrain_set_cell(i, j, val, oval)
            return None
        raise SudokuError(f'set_cell error: {i} {j} {val}')

    def get_cell(self, i, j):
        """get_cell returns the contents of the given cell (which could be None)."""
        if 0 <= i <= 8 and 0 <= j <= 8:
            return self.grid[i][j]
        raise SudokuError(f'get_cell error:{i} {j}')

    def to_string(self, pad='  ', blank='.', newline='\n'):
        """to_string produces a string reresentation of the puzzle."""
        def pp(i, j, blank='.'):
            val = self.get_cell(i, j)
            return str(val) if val is not None else blank
        rows = []
        for row in range(9):
            line = [pp(row, col, blank) for col in range(9)]
            rows.append(pad.join(line))
        return newline.join(rows)


    def pprint(self, pad='  ', blank='.', newline='\n'):
        """pprint pretty prints the puzzle to stdout."""
        print(self.to_string(pad, blank, newline))

    def freedom_set(self, row, col):
        """return the freedom set of the given cell."""
        return self.freedom.freedom_set(row, col)


class Syntax:
    """Syntax defines the terms and rules of the Sudoku game."""

    def __init__(self):
        self.constants = make_constants()
        self.variables = make_variables()

        # maps non-trivial rules to an informative string describing them
        self.explanation = {}
        # dividing the rules into trivial and non trivial is used in getting unsat cores (of non-trivial rules)
        self.trivial_rules = self.make_trivial_rules()
        self.duplicate_rules = self.make_duplicate_rules()
        self.all_rules = self.trivial_rules.copy()
        self.all_rules.extend(self.duplicate_rules)


    def var(self, i, j):
        """var returns the variable that represents the given cell."""
        return self.variables[i][j]


    def make_trivial_rules(self):
        """make_trivial_rules creates the rules that force the variables to range over 1 through 9."""
        # x is between 1 and 9
        def between_1_and_9(x):
            return Terms.yor([Terms.eq(x, self.constants[i+1]) for i in range(9)])
        rules = []
        # Every variable is between 1 and 9 inclusive
        for i in range(9):
            for j in range(9):
                rules.append(between_1_and_9(self.var(i, j)))
        return rules


    def make_duplicate_rules(self):
        """make_duplicate_rules create the list of rules asserting that each row, column and subsquare cannot containn duplicates."""
        rules = []
        # All elements in a row must be distinct
        for i in range(9):
            rule = Terms.distinct([self.var(i, j) for j in range(9)])
            self.explanation[rule] = f'Row {i + 1} cannot contain duplicates'
            rules.append(rule)
        # All elements in a column must be distinct
        for i in range(9):
            rule = Terms.distinct([self.var(j, i) for j in range(9)]) # pylint: disable=W1114
            self.explanation[rule] = f'Column {i + 1} cannot contain duplicates'
            rules.append(rule)
        # All elements in each 3x3 square must be distinct
        def subsquare(row, column):
            rname = {0: 'Top', 1: 'Middle', 2: 'Bottom'}
            cname = {0: 'left', 1: 'center', 2: 'right'}
            return f'{rname[row]}-{cname[column]}'
        for row in range(3):
            for column in range(3):
                rule = Terms.distinct([self.var(i + 3 * row, j + 3 * column) for i in range(3) for j in range(3)])
                self.explanation[rule] = f'{subsquare(row,column)} subsquare cannot contain duplicates'
                rules.append(rule)
        return rules

    def cell_equality(self, i, j, val):
        """cell_equality returns the yices term stating that the given cell equals the given value."""
        return Terms.arith_eq_atom(self.var(i, j), self.constants[val])

    def cell_inequality(self, i, j, val):
        """cell_inequality returns the yices term stating that the given cell differs the given value."""
        return Terms.arith_neq_atom(self.var(i, j), self.constants[val])

    def diagram(self, puzzle):
        """diagram returns the set of yices terms stating that cells in the puzzle contain the their non-None values, skippn cells with None in them."""
        terms = []
        for i in range(9):
            for j in range(9):
                val = puzzle.get_cell(i, j)
                if val is not None:
                    terms.append(self.cell_equality(i, j, val))
        return terms

    def explain(self, terms):
        """explain returns a multiline string explaining the given terms (which should be elements of duplicate_rules."""
        sb = StringBuilder()
        count = 1
        for term in terms:
            sb.append(f'Rule {count}: ').append(self.explanation.get(term)).append('\n')
            count += 1
        return str(sb)



class Cores:
    """Cores area data structure for maintaining, filtering, and ranking unsat cores."""
    def __init__(self, card):
        self.core_map = {}
        self.maximum = card

    def add(self, i, j, val, core):
        """adds the fact that the unsat_core of [i,j] != val is core."""
        key = len(core)
        entry = []
        if key not in self.core_map:
            self.core_map[key] = entry
        else:
            entry = self.core_map[key]
        entry.append(tuple([i, j, val, core]))

    def least(self, count):
        """returns a list of the count smallest cores."""
        retval = []
        counter = 0
        for i in range(self.maximum + 1):
            if i in self.core_map:
                vec = self.core_map[i]
                for v in vec: # pylint: disable=C0103
                    retval.append(v)
                    #print(f'OK: {v[0]} {v[1]} {v[2]}   {len(v[3])} / {self.maximum}')
                    counter += 1
                    if counter >= count:
                        return retval
        return retval
