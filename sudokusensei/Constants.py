"""A collection of constants needed for the UI mainly."""
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

#
TITLE = 'SudokuSensei'

# Pixels around the board
MARGIN = 20

# Pixels between buttons
PAD = 5

# Width of every board cell.
SIDE = 50

# Width and height of the whole board
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9


# Don't count more than these number of models
ALEPH_NOUGHT = 64
