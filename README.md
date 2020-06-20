[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blueviolet.svg)](https://creativecommons.org/licenses/by/4.0/)

# SudukoSensei


This started out as a simple sudoku puzzle solver using the new python bindings for yices.
The bindings are no longer new, so I am moving on to using unsat cores to gives hints etc.

It thus is currently a work in progress.

Probably going to try and beef it up a little so that I can use it (and thus test it a bit better)


## Prerequisites

You will need to install [yices](https://github.com/SRI-CSL/yices2) which can be done by building from source,
or using apt on linux (from our PPA) or homebrew on a mac, the [README.md](https://github.com/SRI-CSL/yices2/blob/master/README.md)
there describes the process.

You will also need the python bindings:
```
pip install yices
```
You need a newish Python, I use the new format strings, so you will need at least 3.6.

## Usage

There is a make file that will build and install the package. Once installed, you start of with an empty board
```
sudokusensei
```
There are a collection of predefined boards in the  [data](https://github.com/ianamason/SudokuSensei/tree/master/sudoku/data) directory,
and you can launch one othe these via
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

Once you have the puppy up for can always generate new puzzles.  I will slowly make the UI more user friendly,
but at the moment I am more interested in generating hard puzzles, and accurately estimating their difficulty.

## Acknowledgments

This project was built on top of the nice python [tutorial](http://newcoder.io/gui/) by [@econchic](http://www.roguelynn.com/)
who is hereby thanked. The tutorial is under the creative commons [license](https://creativecommons.org/licenses/by-sa/3.0/deed.en_US) which does
not appear to be an option in GitHub's license widget, consequently I choose the nearest one I could, if this is a problem let me know.


## References


* [The Math behind Sudoku](http://pi.math.cornell.edu/~mec/Summer2009/Mahmood/Intro.html)

* [Graphical User Interfaces](http://newcoder.io/gui/)

* [Generating difficult Sudoku puzzles quickly](https://dlbeer.co.nz/articles/sudoku.html)
