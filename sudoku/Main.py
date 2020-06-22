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

from .Constants import WIDTH, HEIGHT, PAD
from .SudokuGame import SudokuGame
from .SudokuUI import SudokuUI
from .SudokuLib import parse_arguments

def main():
    """main is the pip entry point."""
    try:

        board_name = parse_arguments()

        game = SudokuGame(board_name)

        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("{0}x{1}".format(WIDTH + 3 * PAD, HEIGHT + 120))
        root.mainloop()
        game.dispose()


    except KeyboardInterrupt:
        sys.exit(0)
