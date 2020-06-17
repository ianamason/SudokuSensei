"""Main is the pip entry point."""
# The non-yices portions of this code base come from:
#
# http://newcoder.io/gui/
#
# where the license is:
#
# https://creativecommons.org/licenses/by-sa/3.0/deed.en_US
#
# I have modified the code as I saw fit to suit my purposes.
# All changes are recorded in the git commits.
#

from tkinter import Tk

import sys
import os.path

import pkg_resources as pkg

from .Constants import WIDTH, HEIGHT
from .SudokuGame import SudokuGame
from .SudokuUI import SudokuUI
from .SudokuLib import parse_arguments

def main():
    """main is the pip entry point."""
    try:

        board_name = parse_arguments()

        if board_name is None:
            board_name = 'empty'

        board_file = pkg.resource_filename('sudoku', f'data/{board_name}.sudoku')

        if not os.path.exists(board_file):
            print(f'No such board: {board_file}')
            return

        game = SudokuGame(board_file)

        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("{0}x{1}".format(WIDTH, HEIGHT + 120))
        root.mainloop()
        game.dispose()


    except KeyboardInterrupt:
        sys.exit(0)
