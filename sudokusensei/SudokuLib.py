"""A library to store useful routines and keep the clutter to a minimum."""

import os.path
import argparse

import pkg_resources as pkg

from yices.Types import Types
from yices.Terms import Terms

from .StringBuilder import StringBuilder

int_t = Types.int_type()

class SudokuError(Exception):
    """An application specific error."""

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

def make_cell_map():
    """constructs an initially empty cell map."""
    cell_map = {}
    for row in range(9):
        for col in range(9):
            cell_map[(row, col)] = set()
    return cell_map

def clear_cell_map(cm):
    """resets a cell map so that it is empty."""
    for row in range(9):
        for col in range(9):
            cm[(row, col)].clear()

def make_value_map():
    """constructs an initially empty mapping from values to cells."""
    v2c = {}
    for val in range(1, 10):
        v2c[val] = set()
    return v2c


class Freedom:
    """Represents simple freedom analysis of a puzzle.

    Each cell is assigned the set of values that it can legally take (irregardless of
    whether they contain a value already). The map is updated as the puzzle is mutated.
    """

    def __init__(self):

        # the set represents the values a cell CANNOT take
        self.freedom = make_cell_map()

        # the set represents the cells that CANNOT contain the 'val'
        self.sofa_map = make_value_map()

    def dump(self, puzzle):
        """prints out the maps for debugging."""
        self.dump_freedom()
        self.dump_sofa(puzzle)

    def dump_freedom(self):
        """prints out the freedom map for debugging."""
        for row in range(9):
            for col in range(9):
                print(f'[{row}, {col}]: {self.freedom_set(row, col)}')


    def dump_sofa(self, puzzle):
        """prints out the sofa map for debugging."""
        for val in range(1, 10):
            print(f'\n{val} (|{puzzle.empty_cells - len(self.sofa_map[val])}|):\t{self.sofa_map[val]}')

    def update_sofa(self, row, col, val, oval):
        """update the sofa map.

        We are changing the contents of [row, col] from oval to val.
        So only sofa_map[oval] and sofa_map[val] will change, and they will only
        change for cells in Regions.influence(row, col).
        """
        assert oval is not None or val is None
        assert oval is not val
        # the empty cells that cannot contain oval (should decrease)
        oval_set = self.sofa_map[oval]
        # the empty cells that cannot contain val (should increase)
        val_set = self.sofa_map[val] if val is not None else None
        for cell in Regions.influence(row, col):
            fset = self.freedom[cell]
            if oval not in fset:
                oval_set.discard(cell)
            if val is not None and val in fset:
                val_set.add(cell)

    def sanity_check_sofa(self, grid):
        """We check that every sofa set agrees with the freedom analysis."""
        for val in range(1, 10):
            for cell in self.sofa_map[val]:
                if grid[cell[0]][cell[1]] is not None:
                    print(f'Wrong: {val} {cell} is not empty.')
                    return False
                if val not in self.freedom[cell]:
                    print(f'Wrong: {val} {cell} is value if free.')
                    return False
        return True

    def constrain_set_cell(self, grid, row, col, val, oval):
        """update the freedom map by adding the fact that cell (row, col) contents is being updated from oval to val."""
        assert grid[row][col] == val  #make sure the grid has already been updated
        self.update(grid, row, col, val, oval)


    def constrain_erase_cell(self, grid, row, col, oval):
        """update the freedom map by removing the fact that cell (row, col) contains oval."""
        assert grid[row][col] is None  #make sure the grid has already been updated
        self.update(grid, row, col, None, oval)

    def update(self, grid, row, col, val, oval):
        """update the freedom map (using Regions) by adding the fact that the cell (row, col) contents is being updated from oval to val."""
        if oval is None and val is not None:
            # the easy case, just need to add the new information
            for cell in Regions.influence(row, col):
                if cell != (row, col):
                    self.freedom[cell].add(val)
                    # the sofa is almost straight forward:
                    if grid[cell[0]][cell[1]] is None:
                        self.sofa_map[val].add(cell)
                    # but we also have to incorporate the fact that [row, col] is no longer empty:
                    for x in range(1, 10):
                        self.sofa_map[x].discard((row, col))
        else:
            # for the freedom map: just recompute the entire region of influence
            for cell in Regions.influence(row, col):
                self.freedom[cell] = Regions.forbidden_set(grid, cell[0], cell[1])
            # once the freedom map is done we can do the sofa map
            self.update_sofa(row, col, val, oval)

    def constrain(self, matrix):
        """computes the cell freedom analysis."""
        for row in range(9):
            for col in range(9):
                self.freedom[(row, col)] = Regions.forbidden_set(matrix, row, col)

    def contains(self, row, col, val):
        """returns true if the val is one of the possible (immediate) choices for the given cell."""
        #remember we are storing the values it cannot take
        return val not in self.freedom[(row, col)]

    def freedom_set(self, row, col):
        """returns the set of possible (immediate) choices for the given cell.

        I.e. the complement of the set we store in the map for the given cell.
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


class Regions:
    """see if caching can speed things up a bit."""

    _block_map = {}

    _row_map = {}

    _column_map = {}

    _influence_map = {}

    @staticmethod
    def block(orow, ocol):
        """returns a list of cells that make up the block the cell belongs to."""
        if 0 <= orow <= 8 and 0 <= ocol <= 8:
            row = 3 * (orow // 3)
            col = 3 * (ocol // 3)
            if (row, col) in Regions._block_map:
                return Regions._block_map[(row, col)]
            retval = frozenset({(r, c) for r in range(row, row + 3) for c in range(col, col + 3)})
            Regions._block_map[(row, col)] = retval
            return retval
        raise SudokuError(f'block error: {orow} {ocol}')

    @staticmethod
    def row(rw):
        """returns the (cached) row at the given index."""
        if 0 <= rw <= 8:
            if rw in Regions._row_map:
                return Regions._row_map[rw]
            retval = frozenset({(rw, c) for c in range(9)})
            Regions._row_map[rw] = retval
            return retval
        raise SudokuError(f'row error: {rw}')

    @staticmethod
    def column(cl):
        """returns the (cached) column at the given index."""
        if 0 <= cl <= 8:
            if cl in Regions._column_map:
                return Regions._column_map[cl]
            retval = frozenset({(r, cl) for r in range(9)})
            Regions._column_map[cl] = retval
            return retval
        raise SudokuError(f'column error: {cl}')

    @staticmethod
    def influence(row, col):
        """returns the (cached) frozen set of cells influenced by the given cell."""
        if 0 <= row <= 8 and  0 <= col <= 8:
            if (row, col) in Regions._influence_map:
                return Regions._influence_map[(row, col)]
            retval = frozenset(Regions.block(row, col).union(Regions.row(row), Regions.column(col)))
            Regions._influence_map[(row, col)] = retval
            return retval
        raise SudokuError(f'influence error: {row} {col}')


    @staticmethod
    def forbidden_set(grid, row, col):
        """returns the set of values that the given cell CANNOT contain in the given grid."""
        influence = Regions.influence(row, col)
        return {grid[cell[0]][cell[1]] for cell in influence if grid[cell[0]][cell[1]] is not None and cell != (row, col)}


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
    def resource2puzzle(name):
        """creates a puzzle from a named resource (the basename of the file in the data directory)."""
        if name is None:
            name = 'empty'
        board_file = pkg.resource_filename('sudokusensei', f'data/{name}.sudoku')
        if not os.path.exists(board_file):
            raise SudokuError(f'No such board: {board_file}')
        return Puzzle.path2puzzle(board_file)


    @staticmethod
    def block(orow, ocol):
        """returns a list of cells that make up the block the cell belongs to."""
        return Regions.block(orow, ocol)

    @staticmethod
    def _block(orow, ocol):
        """returns a list of cells that make up the block the cell belongs to."""
        if 0 <= orow <= 8 and 0 <= ocol <= 8:
            row = 3 * (orow // 3)
            col = 3 * (ocol // 3)
            return [(r, c) for r in range(row, row + 3) for c in range(col, col + 3)]
        raise SudokuError(f'block error: {orow} {ocol}')



    def __init__(self, matrix=None):
        # the grid is the 9x9 matrix
        self.grid = make_grid()
        # the freedom obj mantains the freedom analysis
        self.freedom = Freedom()
        # the number of empty cells (informational carrot)
        self.empty_cells = 81
        # keep track of the cells that each digit resides in (for the sofa analysis)
        self.value_map = make_value_map()

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

    def sanity_check(self, debug):
        """a quick sanity check to make sure the puzzle is not obviously unsolvable."""
        for row in range(9):
            for col in range(9):
                val = self.grid[row][col]
                if val is not None:
                    if not self.freedom.contains(row, col, val):
                        if debug:
                            print(f'Insane: [{row}, {col}]: {val}')
                        return False
        return True

    def sanity_check_sofa(self):
        """we check that the sofa analysis is sane."""
        return self.freedom.sanity_check_sofa(self.grid)


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
                self.empty_cells += 1
                self.grid[i][j] = None
                self.value_map[val].remove((i, j))
                self.freedom.constrain_erase_cell(self.grid, i, j, val)
            return None
        raise SudokuError(f'erase_cell error: {i} {j}')

    def set_cell(self, i, j, val):
        """set_cell set the value of the given cell to the provided value."""
        if 0 <= i <= 8 and 0 <= j <= 8 and 1 <= val <= 9:
            oval = self.grid[i][j]
            if oval != val:
                if oval is None and val is not None:
                    self.empty_cells -= 1
                if oval is not None:
                    self.value_map[oval].remove((i, j))
                self.grid[i][j] = val
                self.value_map[val].add((i, j))
                self.freedom.constrain_set_cell(self.grid, i, j, val, oval)
            return None
        raise SudokuError(f'set_cell error: {i} {j} {val}')

    def get_cell(self, i, j):
        """get_cell returns the contents of the given cell (which could be None)."""
        if 0 <= i <= 8 and 0 <= j <= 8:
            return self.grid[i][j]
        raise SudokuError(f'get_cell error:{i} {j}')

    def dump_value_map(self):
        """print out the current state of the value map"""
        for val in range(1, 10):
            print(f'{val}: {self.value_map[val]}')

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

    def least_free(self):
        """returns the least free cell in the puzzle."""
        return self.freedom.least_free(self.grid)


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
        """make_duplicate_rules create the list of rules asserting that each row, column and block cannot containn duplicates."""
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
        def block(row, column):
            rname = {0: 'Top', 1: 'Middle', 2: 'Bottom'}
            cname = {0: 'left', 1: 'center', 2: 'right'}
            return f'{rname[row]}-{cname[column]}'
        for row in range(3):
            for column in range(3):
                rule = Terms.distinct([self.var(i + 3 * row, j + 3 * column) for i in range(3) for j in range(3)])
                self.explanation[rule] = f'{block(row,column)} block cannot contain duplicates'
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

    def metric(self, debug):
        """ returns my measure of difficulty (should be a number between 0 and roughly 100)."""
        summation = 0
        for i in self.core_map:
            # ugly to have 27 (i.e. |distinct_rules|) hard coded in all these places.
            count = len(self.core_map[i])
            cellv = ((2 * i) / 27) * count
            summation += cellv
            if debug:
                print(f'{i} : {cellv} {count} {summation}')
        return int(summation)
