"""TestMain is a pip entry point for testing purposes."""

import os.path

import pkg_resources as pkg

from .SudokuLib import parse_arguments, Puzzle
from .SudokuGame import SudokuGame
from .SudokuSolver import SudokuSolver
from .SudokuGenerator import solve, choose_solution

def main():
    """main is the pip entry point."""

    board_name = parse_arguments()

    if board_name is None:
        puzzle = Puzzle()
        choose_solution(puzzle)
        puzzle.pprint()
        print(f'#empty_cells = {puzzle.empty_cells}')
        return

    board_file = pkg.resource_filename('sudoku', f'data/{board_name}.sudoku')

    if not os.path.exists(board_file):
        print(f'No such board: {board_file}')
        return

    game = SudokuGame(board_file)

    game.start()

    solution = Puzzle()

    game.puzzle.pprint()

    diff = [0]

    smt_solution = SudokuSolver(game).solve()

    if smt_solution is None:
        return

    solve(game.puzzle, solution, diff)

    print('\n')

    solution.pprint()

    print(f'Difficulty: {diff[0]}')
    print(f'#empty_cells = {game.puzzle.empty_cells}')

    print(solution.agree(smt_solution))
