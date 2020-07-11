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
[claimed](https://www.conceptispuzzles.com/index.aspx?uri=info/article/424) is the hardest one possible, see the screen shot above.

Once you have the puppy up you can always generate new puzzles.  The options tab will allow you to attempt to specify the
level of difficulty of the generated puzzle.

![Options](img/options-tab.png?raw_true)

You can even use the tool to create your own Sudoku puzzles, just start with an empty board, and make use of the `Show > # Solutions`
feature to make sure your puzzle has a *unique* solution. You can save it from the options tab.

## Bells and Whistles  (AKA Freeping Creaturism)

The tool can do lots of things. Instead of writing a well structured guide, I am going to just list the features
as they occur to me. Sorry.

### Notes

You can make notes by simply entering multiple numbers, the same number entered twice will toggle that number in or out.
If you are really lazy you can start off your notes from the freedom analysis (`Show > Freedom Notes`).

![Freedom-Notes](img/freedom-notes.png?raw_true)


### Check 

You can see if you are on the right track by pressing the `Check` button. The UI is in a primitive state, and maybe
I will get around to highlighting the wrong squares rather than just *naming* them.

### Freedom Analysis

The freedom analysis assigns to each empty cell the set of legal possibilities for that cell. I.e. choices that do 
not obviously violate the uniqueness axioms.
You can look at the freedom analysis of the puzzle via `Show > Freedom`, and get rid of them via
`Clear > Freedom`.

![Freedom](img/freedom.png?raw_true)

### Least Free

As the most primitve kind of hint, one can ask for the least free cell via `Show > Least Free` which will highlight
the cell with the smallest freedom set.

### Hints

You can ask for a hint. Hints are hard. What we do is compute the minimal unsat core for each empty cell (with
some optimizations: see the `cutoff` in the options tab) and point out a cell with the smallest such core. This is usually a good indication that 
the cell can be solved relatively easily by a human. Though of course wth really hard puzzles these are still really hard
to solve. If you on debugging you will even see (in the console) the actual answer. But don't cheat, you won'y feel better for it.

### Counting Solutions

A legal puzzle should have exactly one solution, but when you are designing your own you may have many solutions.
You can count the number of solutions via `Show > # Solutions`. This computation could take a long time, so we have 
a simple upper bound cutoff called `aleph_nought` that you can configure in the options tab.

### Estimating Difficulty

Estimating the difficulty of a puzzle is also hard. We provide three, two are branch-difficulty measures of two 
different backtracking solution search algorithms presented in [[3]](https://dlbeer.co.nz/articles/sudoku.html).
These are somewhat adhoc in congruent puzzles (via the natural symmetries) will have different difficulties.
`Show > Difficulty (No Sofa)` and `Show > Difficulty (Sofa)` give these values (ranging from 0 to above 1000).
We also present another metric (that we cooked up) but this takes time to compute, so be patient. It
is a metric, and is basically  proportional to the sum of the sizes of all the minimal unsat cores. This is
computationally expensive to calculate, but does provide me with a good example for which to use threads and 
thread safe yices, so I will probably spend some more time on this in the not to distant future.

### Generating Difficult Puzzles

Generating difficult puzzles quickly is difficult. 
We again rely on the earlier work of Daniel Beer.
To generate a new puzzle just press the `New` button.
The options tab has several parameters that affect what happens under the
hood once this button is pressed. You can choose the language (`C` or `Python`)
in which the search takes place, the tye of search algorithm used (`Sofa` or `No Sofa`).
The target difficulty, and how long one searches for a suitable puzzle.
Not all the Python options have been implemented (In particular Sofa search). But 
there is not much coding left.

*Warning* using Python as the language requires patience, and being in debug mode
is good, so one can see the progress being made.


##  Solving

You can solve the current puzzle by just pressing the `Solve` button. This uses the SMT solver, rather than the
two other techniques. Solving is easy, so not much to say here.

## Acknowledgments

This project was built on top of the nice python tutorial [[2]](http://newcoder.io/gui/) by [@econchic](http://www.roguelynn.com/)
who is hereby thanked. The tutorial is under the creative commons [license](https://creativecommons.org/licenses/by-sa/3.0/deed.en_US) which does
not appear to be an option in GitHub's license widget, consequently I choose the nearest one I could, if this is a problem let me know.


## References


* [[1]](http://pi.math.cornell.edu/~mec/Summer2009/Mahmood/Intro.html) The Math behind Sudoku. Cornell Math Explorer's Club.

* [[2]](http://newcoder.io/gui/) Graphical User Interfaces. Lynn Root.

* [[3]](https://dlbeer.co.nz/articles/sudoku.html) Generating difficult Sudoku puzzles quickly. Daniel Beer.
