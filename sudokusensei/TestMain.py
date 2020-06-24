"""TestMain is a pip entry point for testing purposes."""

import os.path

import pkg_resources as pkg

from .SudokuLib import parse_arguments, Puzzle
from .SudokuGame import SudokuGame
from .SudokuSolver import SudokuSolver
from .SudokuGenerator import SudokuGenerator, choose_solution

def test0():
    """Quick test of the solution generation code."""
    puzzle = Puzzle()
    choose_solution(puzzle)
    if not puzzle.sanity_check(True):
        puzzle.freedom.dump(puzzle)
    puzzle.pprint()
    print(f'Sanity: {puzzle.sanity_check(True)} #empty_cells = {puzzle.empty_cells}')

def main():
    """main is the pip entry point."""

    board_name = parse_arguments()

    generator = SudokuGenerator()

    if board_name is None:
        if False: # pylint: disable=W0125
            test0()
            return
        score, puzzle = generator.generate()
        puzzle.pprint()
        print(f'Difficulty: {score} Target: {generator.options.difficulty} Empty: {puzzle.empty_cells} ')
        return

    board_file = pkg.resource_filename('sudoku', f'data/{board_name}.sudoku')

    if not os.path.exists(board_file):
        print(f'No such board: {board_file}')
        return

    game = SudokuGame(board_file)

    game.start()

    solution = Puzzle()

    game.puzzle.pprint()

    print(f'Sanity check: {game.puzzle.sanity_check()}')

    diff = [0]

    smt_solution = SudokuSolver(game).solve()

    if smt_solution is None:
        return

    generator.solve(game.puzzle, solution, diff)

    print('\n')

    solution.pprint()

    print(f'Difficulty: {diff[0]}')
    print(f'#clues = {81 - game.puzzle.empty_cells}')

    print(solution.agree(smt_solution))
