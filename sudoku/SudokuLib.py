"""A library to store useful routines and keep the clutter to a minimum."""

from yices.Types import Types
from yices.Terms import Terms


int_t = Types.int_type()

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


class SudokuError(Exception):
    """An application specific error."""


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


    def __init__(self, matrix=None):
        self.grid = make_grid()
        if matrix is not None:
            for i in range(9):
                for j in range(9):
                    val = matrix[i][j]
                    if val is not None:
                        self.set_cell(i, j, val)

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
            self.grid[i][j] = None
            return None
        raise SudokuError(f'erase_cell error: {i} {j}')

    def set_cell(self, i, j, val):
        """set_cell set the value of the given cell to the provided value."""
        if 0 <= i <= 8 and 0 <= j <= 8 and 1 <= val <= 9:
            self.grid[i][j] = val
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
