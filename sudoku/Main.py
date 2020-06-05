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

import argparse
import sys
import pkg_resources as pkg

from .Constants import BOARDS, WIDTH, HEIGHT
from .SudokuGame import SudokuGame
from .SudokuUI import SudokuUI


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
                            choices=BOARDS,
                            required=False)

    # Creates a dictionary of keys = argument flag, and value = argument
    args = vars(arg_parser.parse_args())
    return args['board']




def main():
    """main is the pip entry point."""
    try:

        board_name = parse_arguments()

        board_file = pkg.resource_filename('sudoku', f'data/{board_name}.sudoku')

        if board_name is not None:
            board_fp = open(board_file, 'r')
        else:
            board_fp = None

        game = SudokuGame(board_fp)

        if board_fp is not None:
            board_fp.close()

        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("{0}x{1}".format(WIDTH, HEIGHT + 40))
        root.mainloop()
        game.dispose()


    except KeyboardInterrupt:
        sys.exit(0)
