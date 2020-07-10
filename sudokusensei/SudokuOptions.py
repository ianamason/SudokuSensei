"""For handling what's going on under the hood."""
import tkinter as tk
import os.path

from tkinter import filedialog

from pathlib import Path

import pkg_resources as pkg

from .DB import db_debug

class Options:    # pylint: disable=R0902
    """For retaining the user's chosen options."""

    def __init__(self):
        # turns on all sorts of whingeing and whining
        self.debug = False
        # allows one to edit the "original" puzzle squares
        self.edit = False
        # uses the C versions of the slow routines.
        self.use_c = True
        # use set oriented freedom in the solving phase, which can eliminate
        # a lot of backtracking (and hence the difficulty metric).
        self.sofa = False
        # the desired metric, note sofa vs no sofa metrics are very different.
        # sofa numbers are genrally a lot smaller.
        self.difficulty = 400
        # game generation iterations.
        self.iterations = 200
        # we compute the cores for all empty cells, then cream off the smallest "cutoff"
        # ones, and reduce them further.
        self.unsat_core_cutoff = 5
        # aleph_nought
        self.aleph_nought = 64


PADX = 20
PADY = 20

class SudokuOptions(tk.Toplevel):
    """The UI for letting the user (i.e. me) configure what is going on under the hood."""

    def __init__(self, game_ui, title, options):
        tk.Toplevel.__init__(self)
        width = 600
        height = 600
        self.options = options
        self.title(title)
        self.game_ui = game_ui
        self.geometry(f'{width}x{height}')
        self.minsize(width, height)
        self.maxsize(width, height)

        self.checkboxes = tk.Frame(self)
        self.checkboxes.grid(row=0, column=0, sticky='nsew')

        self.buttons = tk.Frame(self)
        self.buttons.grid(row=1, column=0, sticky='nsew')


        self._create_debug_controls(0)
        self._create_edit_controls(1)
        self._create_language_controls(2)
        self._create_sofa_controls(3)
        self._create_difficulty_controls(4)
        self._create_iterations_controls(5)
        self._create_cutoff_controls(6)
        self._create_aleph_nought_controls(7)

        self._create_buttons()


    def _create_buttons(self):
        save_button = tk.Button(self.buttons, text="Save", command=self.__save_puzzle)
        load_button = tk.Button(self.buttons, text="Load", command=self.__load_puzzle)
        ok_button = tk.Button(self.buttons, text="OK", command=self.__ok)
        save_button.grid(row=1, column=1, sticky="w", padx=PADX, pady=PADY)
        load_button.grid(row=1, column=2, sticky="e", padx=PADX, pady=PADY)
        ok_button.grid(row=1, column=3, sticky="e", padx=PADX, pady=PADY)

    def _get_resource_directory(self, saving=False):
        if not saving or self.options.debug:
            empty_file = pkg.resource_filename('sudokusensei', 'data/empty.sudoku')
            if os.path.exists(empty_file):
                return os.path.dirname(empty_file)
        home = str(Path.home())
        return home

    def __ok(self):
        self.destroy()

    def __save_puzzle(self):
        """don't use the data directory as the default when writing (since it may be write protected)"""
        filename = filedialog.asksaveasfilename(initialdir=self._get_resource_directory(True), filetypes=[('Sudoku', '*.sudoku')], initialfile='game.sudoku')
        if filename is not None and len(filename) > 0:
            self.game_ui.save_game(filename)
            self.destroy()


    def __load_puzzle(self):
        filename = filedialog.askopenfilename(initialdir=self._get_resource_directory(), initialfile='game.sudoku')
        if filename is not None and len(filename) > 0 and os.path.exists(filename):
            self.game_ui.load_game(filename)
            self.destroy()


    def _create_debug_controls(self, row):
        debug = tk.BooleanVar()
        debug.set(self.options.debug)

        def update_debug():
            self.options.debug = debug.get()
            db_debug(self.options.debug)

        debugging = tk.Label(self.checkboxes, text="Debugging: ")
        debugging.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        use_debug = tk.Radiobutton(self.checkboxes, text='Debug', variable=debug, value=True, command=update_debug)
        use_debug.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        no_debug = tk.Radiobutton(self.checkboxes, text='No Debug', variable=debug, value=False, command=update_debug)
        no_debug.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)

    def _create_edit_controls(self, row):
        edit = tk.BooleanVar()
        edit.set(self.options.edit)

        def update_edit():
            self.options.edit = edit.get()

        editing = tk.Label(self.checkboxes, text="Editing: ")
        editing.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        use_edit = tk.Radiobutton(self.checkboxes, text='Editing', variable=edit, value=True, command=update_edit)
        use_edit.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        no_edit = tk.Radiobutton(self.checkboxes, text='Not Editing', variable=edit, value=False, command=update_edit)
        no_edit.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)


    def _create_language_controls(self, row):
        cvar = tk.BooleanVar()
        cvar.set(self.options.use_c)

        def update_language():
            self.options.use_c = cvar.get()

        language = tk.Label(self.checkboxes, text="Search Language: ")
        language.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        use_c = tk.Radiobutton(self.checkboxes, text='C', variable=cvar, value=True, command=update_language)
        use_c.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        use_python = tk.Radiobutton(self.checkboxes, text='Python', variable=cvar, value=False, command=update_language)
        use_python.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)


    def _create_sofa_controls(self, row):
        sofa = tk.BooleanVar()
        sofa.set(self.options.sofa)

        def update_sofa():
            self.options.sofa = sofa.get()

        strategy = tk.Label(self.checkboxes, text="Search Strategy: ")
        strategy.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        use_sofa = tk.Radiobutton(self.checkboxes, text='SOFA', variable=sofa, value=True, command=update_sofa)
        use_sofa.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        no_sofa = tk.Radiobutton(self.checkboxes, text='No SOFA', variable=sofa, value=False, command=update_sofa)
        no_sofa.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)


    def _create_difficulty_controls(self, row):
        difficulty = tk.IntVar()
        difficulty.set(self.options.difficulty)

        def update_difficulty():
            self.options.difficulty = difficulty.get()

        target = tk.Label(self.checkboxes, text="Target Difficulty: ")
        target.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        diff_400 = tk.Radiobutton(self.checkboxes, text='400', variable=difficulty, value=400, command=update_difficulty)
        diff_400.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        diff_600 = tk.Radiobutton(self.checkboxes, text='600', variable=difficulty, value=600, command=update_difficulty)
        diff_600.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)

        diff_800 = tk.Radiobutton(self.checkboxes, text='800', variable=difficulty, value=800, command=update_difficulty)
        diff_800.grid(row=row, column=3, sticky='w', padx=PADX, pady=PADY)

    def _create_iterations_controls(self, row):
        iterations = tk.IntVar()
        iterations.set(self.options.iterations)

        def update_iterations():
            self.options.iterations = iterations.get()

        search = tk.Label(self.checkboxes, text="Search Iterations: ")
        search.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        iter_200 = tk.Radiobutton(self.checkboxes, text='200', variable=iterations, value=200, command=update_iterations)
        iter_200.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        iter_400 = tk.Radiobutton(self.checkboxes, text='400', variable=iterations, value=400, command=update_iterations)
        iter_400.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)

        iter_800 = tk.Radiobutton(self.checkboxes, text='800', variable=iterations, value=800, command=update_iterations)
        iter_800.grid(row=row, column=3, sticky='w', padx=PADX, pady=PADY)

        iter_1000 = tk.Radiobutton(self.checkboxes, text='1000', variable=iterations, value=1000, command=update_iterations)
        iter_1000.grid(row=row, column=4, sticky='w', padx=PADX, pady=PADY)


    def _create_cutoff_controls(self, row):
        cutoff = tk.IntVar()
        cutoff.set(self.options.unsat_core_cutoff)

        def update_cutoff():
            self.options.unsat_core_cutoff = cutoff.get()

        search = tk.Label(self.checkboxes, text="Unsat Core Cutoff: ")
        search.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        iter_5 = tk.Radiobutton(self.checkboxes, text='5', variable=cutoff, value=5, command=update_cutoff)
        iter_5.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        iter_10 = tk.Radiobutton(self.checkboxes, text='10', variable=cutoff, value=10, command=update_cutoff)
        iter_10.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)

        iter_20 = tk.Radiobutton(self.checkboxes, text='20', variable=cutoff, value=20, command=update_cutoff)
        iter_20.grid(row=row, column=3, sticky='w', padx=PADX, pady=PADY)

        iter_50 = tk.Radiobutton(self.checkboxes, text='50', variable=cutoff, value=50, command=update_cutoff)
        iter_50.grid(row=row, column=4, sticky='w', padx=PADX, pady=PADY)


    def _create_aleph_nought_controls(self, row):
        aleph_nought = tk.IntVar()
        aleph_nought.set(self.options.aleph_nought)

        def update_aleph_nought():
            self.options.aleph_nought = aleph_nought.get()

        label = tk.Label(self.checkboxes, text="Aleph Nought: ")
        label.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        aleph_nought_64 = tk.Radiobutton(self.checkboxes, text='2^6', variable=aleph_nought, value=64, command=update_aleph_nought)
        aleph_nought_64.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        aleph_nought_256 = tk.Radiobutton(self.checkboxes, text='2^8', variable=aleph_nought, value=256, command=update_aleph_nought)
        aleph_nought_256.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)

        aleph_nought_1024 = tk.Radiobutton(self.checkboxes, text='2^10', variable=aleph_nought, value=1024, command=update_aleph_nought)
        aleph_nought_1024.grid(row=row, column=3, sticky='w', padx=PADX, pady=PADY)

        aleph_nought_4096 = tk.Radiobutton(self.checkboxes, text='2^12', variable=aleph_nought, value=4096, command=update_aleph_nought)
        aleph_nought_4096.grid(row=row, column=4, sticky='w', padx=PADX, pady=PADY)
