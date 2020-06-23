"""For handling what's going on under the hood."""
import tkinter as tk


class Options:
    """For retaining the user's chosen options."""

    def __init__(self):
        self.use_c = False
        self.sofa = False
        self.difficulty = 400
        self.iterations = 200


class SudokuOptions(tk.Toplevel):
    """For configuring what is going on under the hood."""

    def __init__(self, title, options):
        tk.Toplevel.__init__(self)
        self.options = options
        self.title(title)

        self.geometry('400x100')
        self.minsize(400, 100)
        self.maxsize(425, 250)

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky='nsew')

        self._create_language_controls()
        self._create_sofa_controls()
        self._create_difficulty_controls()
        self._create_iterations_controls()


    def _create_language_controls(self):
        cvar = tk.BooleanVar()
        cvar.set(self.options.use_c)

        def update_language():
            self.options.use_c = cvar.get()

        language = tk.Label(self.frame, text="Search Language: ")
        language.grid(row=0, column=0, sticky='w')

        use_c = tk.Radiobutton(self.frame, text='C', variable=cvar, value=True, command=update_language)
        use_c.grid(row=0, column=1)

        use_python = tk.Radiobutton(self.frame, text='Python', variable=cvar, value=False, command=update_language)
        use_python.grid(row=0, column=2)


    def _create_sofa_controls(self):
        sofa = tk.BooleanVar()
        sofa.set(self.options.sofa)

        def update_sofa():
            self.options.sofa = sofa.get()

        strategy = tk.Label(self.frame, text="Search Strategy: ")
        strategy.grid(row=1, column=0, sticky='w')

        use_sofa = tk.Radiobutton(self.frame, text='SOFA', variable=sofa, value=True, command=update_sofa)
        use_sofa.grid(row=1, column=1)

        no_sofa = tk.Radiobutton(self.frame, text='No SOFA', variable=sofa, value=False, command=update_sofa)
        no_sofa.grid(row=1, column=2)


    def _create_difficulty_controls(self):
        difficulty = tk.IntVar()
        difficulty.set(self.options.difficulty)

        def update_difficulty():
            self.options.difficulty = difficulty.get()

        target = tk.Label(self.frame, text="Target Difficulty: ")
        target.grid(row=2, column=0, sticky='w')

        diff_400 = tk.Radiobutton(self.frame, text='400', variable=difficulty, value=400, command=update_difficulty)
        diff_400.grid(row=2, column=1)

        diff_600 = tk.Radiobutton(self.frame, text='600', variable=difficulty, value=600, command=update_difficulty)
        diff_600.grid(row=2, column=2)

        diff_800 = tk.Radiobutton(self.frame, text='800', variable=difficulty, value=800, command=update_difficulty)
        diff_800.grid(row=2, column=3)

    def _create_iterations_controls(self):
        iterations = tk.IntVar()
        iterations.set(self.options.iterations)

        def update_iterations():
            self.options.iterations = iterations.get()

        search = tk.Label(self.frame, text="Search Iterations: ")
        search.grid(row=3, column=0, sticky='w')

        iter_200 = tk.Radiobutton(self.frame, text='200', variable=iterations, value=200, command=update_iterations)
        iter_200.grid(row=3, column=1)

        iter_400 = tk.Radiobutton(self.frame, text='400', variable=iterations, value=400, command=update_iterations)
        iter_400.grid(row=3, column=2)

        iter_800 = tk.Radiobutton(self.frame, text='800', variable=iterations, value=800, command=update_iterations)
        iter_800.grid(row=3, column=3)

        iter_1000 = tk.Radiobutton(self.frame, text='1000', variable=iterations, value=1000, command=update_iterations)
        iter_1000.grid(row=3, column=4)
