[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blueviolet.svg)](https://creativecommons.org/licenses/by/4.0/)
[![PyPI version](https://badge.fury.io/py/sudokusensei.svg)](https://badge.fury.io/py/sudokusensei)
[![PyPI Statistics](https://img.shields.io/pypi/dm/sudokusensei.svg)](https://pypistats.org/packages/sudokusensei)

# SudukoSensei

![SudokuSensei](img/sudokusensei.png?raw_true)

A Playground for testing our SMT's python bindings, learning tkinter, solving Sudoku puzzles, trying to give hints, and delving into
the intracies of generating sudoku puzzles, measuring their difficulty, and the list goes on.

The tool is in a pretty good state. Play with it. Let me know what else it needs, or needs explaining.


## Prerequisites

You need a newish Python, I quite like and make use of the new format strings, so you will need at least 3.6.

The software is packaged as a pip package, but to install it successfully you will *first*
need to install [yices](https://github.com/SRI-CSL/yices2) which can be done by building from source,
or using apt on linux (from our PPA) or homebrew on a mac, the [README.md](https://github.com/SRI-CSL/yices2/blob/master/README.md)
there describes the process.

So you can either do
```
pip install sudokusensei
```
or if you want to hack, clone this repository and do
```
make develop
```

## Usage

There is a make file that will build and install the package. Once installed, you start of with an empty board
```
sudokusensei
```
If you press the options button you will be able to load one of our many predefined boards in the
[data](https://github.com/ianamason/SudokuSensei/tree/master/sudoku/data) directory,
and you can also directly launch one of these via
```
sudokusensei --board <board base name>
```
For example:
```
sudokusensei --board  sofa
```
will start you off with the puzzle that Daniel Beer (@dlbeer) mentions in showing the difference in difficulty
between sofa and non-sofa search, see the references below.

Another example would be
```
sudokusensei --board  hardest
```
which will start you off with the puzzle that Finnish mathematician [Arto Inkala](http://www.aisudoku.com/index_en.html)
[claimed](https://www.conceptispuzzles.com/index.aspx?uri=info/article/424) is the hardest one possible.

Once you have the puppy up you can always generate new puzzles.  The options tab will allow you to attempt to specify the
level of difficulty of the generated puzzle.

You can even use the tool to create your own Sudoku puzzles, just start with an empty board, and make use of the `Show > # Solutions`
feature to make sure your puzzle has a *unique* solution. You can save it from the options tab.

## Bells and Whistles  (AKA Freeping Creaturism)

The tool can do lots of things. Instead of writing a well structured guide, I am going to just list the features
as they occur to me. Sorry.

* Freedom Analysis: you can look at the freedom analysis of the puzzle via `Show > Freedom`, and get rid of them via
`Clear > Freedom`.

* Notes: you can make notes by simply entering multiple numbers, the same number entered twice will toggle that number in or out.
If you are really lazy you can start off your notes from the freedom analysis (`Show > Freedom Notes`).


## Acknowledgments

This project was built on top of the nice python [tutorial](http://newcoder.io/gui/) by [@econchic](http://www.roguelynn.com/)
who is hereby thanked. The tutorial is under the creative commons [license](https://creativecommons.org/licenses/by-sa/3.0/deed.en_US) which does
not appear to be an option in GitHub's license widget, consequently I choose the nearest one I could, if this is a problem let me know.


## References


* [[1]](http://pi.math.cornell.edu/~mec/Summer2009/Mahmood/Intro.html) The Math behind Sudoku. Cornell Math Explorer's Club.

* [[2]](http://newcoder.io/gui/) Graphical User Interfaces. Lynn Root.

* [[3]](https://dlbeer.co.nz/articles/sudoku.html) Generating difficult Sudoku puzzles quickly. Daniel Beer.
