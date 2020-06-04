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

## Usage (out of date)

So not a lot of brain power was spent making this a watertight work. But if you start of with an empty board
```
./sudokusolver
```
you can add entries one by one, and then solve. Clear the solution and continue to add entries. Or if you wish you
can clear the entries too.  There are a couple of built in boards, so you can start from one like so:
```
./sudokusolver --board debug
./sudokusolver --board n00b
./sudokusolver --board l33t
```
add a few entries and then solve. Seems like the `l33t` board has 158 solutions, which I think means it is not a
legal puzzle.

You can also ask for the number of solutions, but if there are more than 64 we do not persist, and just return 64.

## Acknowledgments

This project was built on top of the nice python [tutorial](http://newcoder.io/gui/) by [@econchic](http://www.roguelynn.com/)
who is hereby thanked. The tutorial is under the creative commons [license](https://creativecommons.org/licenses/by-sa/3.0/deed.en_US) which does
not appear to be an option in GitHub's license widget, consequently I choose the nearest one I could, if this is a problem let me know.


## References


[The Math behind Sudoku](http://pi.math.cornell.edu/~mec/Summer2009/Mahmood/Intro.html)
[Graphical User Interfaces](http://newcoder.io/gui/)
[Arel's Sudoku Generator](https://github.com/arel/arels-sudoku-generator.git)
[Generating difficult Sudoku puzzles quickly](https://dlbeer.co.nz/articles/sudoku.html)
