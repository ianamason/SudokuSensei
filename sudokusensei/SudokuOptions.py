"""For handling what's going on under the hood."""
import tkinter as tk

from .DB import db_debug

class Options:
    """For retaining the user's chosen options."""

    def __init__(self):
        self.debug = False
        self.use_c = True
        self.sofa = False
        self.difficulty = 400
        self.iterations = 200


PADX = 20
PADY = 20

class SudokuOptions(tk.Toplevel):
    """The UI for letting the user (i.e. me) configure what is going on under the hood."""

    def __init__(self, title, options):
        tk.Toplevel.__init__(self)
        self.options = options
        self.title(title)

        self.geometry('600x350')
        self.minsize(600, 350)
        self.maxsize(600, 350)

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky='nsew')

        self._create_debug_controls(0)
        self._create_language_controls(1)
        self._create_sofa_controls(2)
        self._create_difficulty_controls(3)
        self._create_iterations_controls(4)

    def _create_debug_controls(self, row):
        debug = tk.BooleanVar()
        debug.set(self.options.debug)

        def update_debug():
            self.options.debug = debug.get()
            db_debug(self.options.debug)

        debugging = tk.Label(self.frame, text="Debugging: ")
        debugging.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        use_debug = tk.Radiobutton(self.frame, text='Debug', variable=debug, value=True, command=update_debug)
        use_debug.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        no_debug = tk.Radiobutton(self.frame, text='No Debug', variable=debug, value=False, command=update_debug)
        no_debug.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)


    def _create_language_controls(self, row):
        cvar = tk.BooleanVar()
        cvar.set(self.options.use_c)

        def update_language():
            self.options.use_c = cvar.get()

        language = tk.Label(self.frame, text="Search Language: ")
        language.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        use_c = tk.Radiobutton(self.frame, text='C', variable=cvar, value=True, command=update_language)
        use_c.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        use_python = tk.Radiobutton(self.frame, text='Python', variable=cvar, value=False, command=update_language)
        use_python.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)


    def _create_sofa_controls(self, row):
        sofa = tk.BooleanVar()
        sofa.set(self.options.sofa)

        def update_sofa():
            self.options.sofa = sofa.get()

        strategy = tk.Label(self.frame, text="Search Strategy: ")
        strategy.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        use_sofa = tk.Radiobutton(self.frame, text='SOFA', variable=sofa, value=True, command=update_sofa)
        use_sofa.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        no_sofa = tk.Radiobutton(self.frame, text='No SOFA', variable=sofa, value=False, command=update_sofa)
        no_sofa.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)


    def _create_difficulty_controls(self, row):
        difficulty = tk.IntVar()
        difficulty.set(self.options.difficulty)

        def update_difficulty():
            self.options.difficulty = difficulty.get()

        target = tk.Label(self.frame, text="Target Difficulty: ")
        target.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        diff_400 = tk.Radiobutton(self.frame, text='400', variable=difficulty, value=400, command=update_difficulty)
        diff_400.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        diff_600 = tk.Radiobutton(self.frame, text='600', variable=difficulty, value=600, command=update_difficulty)
        diff_600.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)

        diff_800 = tk.Radiobutton(self.frame, text='800', variable=difficulty, value=800, command=update_difficulty)
        diff_800.grid(row=row, column=3, sticky='w', padx=PADX, pady=PADY)

    def _create_iterations_controls(self, row):
        iterations = tk.IntVar()
        iterations.set(self.options.iterations)

        def update_iterations():
            self.options.iterations = iterations.get()

        search = tk.Label(self.frame, text="Search Iterations: ")
        search.grid(row=row, column=0, sticky='w', padx=PADX, pady=PADY)

        iter_200 = tk.Radiobutton(self.frame, text='200', variable=iterations, value=200, command=update_iterations)
        iter_200.grid(row=row, column=1, sticky='w', padx=PADX, pady=PADY)

        iter_400 = tk.Radiobutton(self.frame, text='400', variable=iterations, value=400, command=update_iterations)
        iter_400.grid(row=row, column=2, sticky='w', padx=PADX, pady=PADY)

        iter_800 = tk.Radiobutton(self.frame, text='800', variable=iterations, value=800, command=update_iterations)
        iter_800.grid(row=row, column=3, sticky='w', padx=PADX, pady=PADY)

        iter_1000 = tk.Radiobutton(self.frame, text='1000', variable=iterations, value=1000, command=update_iterations)
        iter_1000.grid(row=row, column=4, sticky='w', padx=PADX, pady=PADY)
