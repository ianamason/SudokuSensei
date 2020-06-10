"""TestMain is a pip entry point for testing purposes."""

import pkg_resources as pkg

from .SudokuLib import parse_arguments, Puzzle
from .SudokuGame import SudokuGame
from .SudokuSolver import SudokuSolver
from .SudokuGenerator import solve

def main():
    """main is the pip entry point."""
    board_name = parse_arguments()

    if board_name is None:
        board_name = 'empty'

    board_file = pkg.resource_filename('sudoku', f'data/{board_name}.sudoku')

    game = SudokuGame(board_file)

    game.start()

    solution = Puzzle()

    game.puzzle.pprint()

    diff = [0]

    smt_solution = SudokuSolver(game).solve()

    if smt_solution is None:
        return

    solve(game.puzzle, solution, diff)

    solution.pprint()

    print(f'Difficulty: {diff[0]}')

    print(solution.agree(smt_solution))
