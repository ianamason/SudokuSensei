"""SudokuUI is the main frame of the game. """
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

import tkinter as tk

from tkinter import messagebox

from .Constants import DEBUG, TITLE, WIDTH, HEIGHT, PAD, MARGIN, SIDE, ALEPH_NOUGHT

delta = SIDE / 4

"""handle the layout of freedom entries in a cell."""
DELTA = {
    1: (delta, delta),
    2: (2*delta, delta),
    3: (3*delta, delta),
    4: (delta, 2*delta),
    5: (2*delta, 2*delta),
    6: (3*delta, 2*delta),
    7: (delta, 3*delta),
    8: (2*delta, 3*delta),
    9: (3*delta, 3*delta),
}

class SudokuUI(tk.Frame): # pylint: disable=R0901,R0902
    """The Tkinter UI, responsible for drawing the board and accepting user input."""

    font = ('Arial', 32)

    free_font = ('Arial', 10)

    def __init__(self, parent, game):
        tk.Frame.__init__(self, parent)
        self.game = game
        self.parent = parent
        self.row, self.col = -1, -1

        self.__init_ui(parent)


    def __init_ui(self, parent):
        parent.title(TITLE)

        # split the UI into a message panel, canvas, and a control panel
        self.messages = tk.Frame(parent, width=WIDTH, height=50)
        self.controls = tk.Frame(parent, width=WIDTH, height=100)
        self.canvas = tk.Canvas(parent, width=WIDTH, height=HEIGHT)

        self.messages.grid(column=0, row=0, sticky="we")
        self.canvas.grid(column=0, row=1, sticky="we", padx=PAD)
        self.controls.grid(column=0, row=2, sticky="we")

        self.message_text = tk.StringVar()
        self.message_text.set("Welcome to Sudoku Sensei")

        self.messagebox = tk.Label(self.messages, textvariable=self.message_text)
        self.messagebox.pack(side="top", fill="both", pady=2*PAD, expand=True)

        self.clear_var = tk.StringVar(parent)
        self.clear_choices = ['', 'Puzzle', 'Solution']
        self.clear_var.set('')
        self.clear_var.trace(callback=self.__dispatch_clear_choice, mode='w')

        self.show_var = tk.StringVar(parent)
        self.show_choices = ['', 'Least Free', 'Hint', '# Solutions', 'Freedom', 'Difficulty', 'Sofa', 'Sanity Check']
        self.show_var.set('')
        self.show_var.trace(callback=self.__dispatch_show_choice, mode='w')

        self._create_controls(self.controls)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind('<Button-1>', self.__cell_clicked)
        self.canvas.bind('<Key>', self.__key_pressed)



    def _create_controls(self, parent):


        clear_label = tk.Label(parent, text="Clear ...")
        show_label = tk.Label(parent, text="Show ...")

        clear_choice = tk.OptionMenu(parent, self.clear_var, *self.clear_choices)
        clear_choice.config(width=10)

        show_choice = tk.OptionMenu(parent, self.show_var, *self.show_choices)
        show_choice.config(width=10)

        check_button = tk.Button(parent, text="Check", command=self.__check_puzzle)
        new_button = tk.Button(parent, text="New Game", command=self.__new_puzzle)
        solve_button = tk.Button(parent, text="Solve", command=self.__solve_puzzle)

        clear_label.grid(row=0, column=1, sticky="we")
        show_label.grid(row=0, column=2, sticky="we")

        clear_choice.grid(row=1, column=1, sticky="we")
        show_choice.grid(row=1, column=2, sticky="we")
        check_button.grid(row=1, column=3, sticky="we")
        new_button.grid(row=1, column=4, sticky="we")
        solve_button.grid(row=1, column=5, sticky="we")


    def __dispatch_show_choice(self, *args): # pylint: disable=W0613
        desire = self.show_var.get()
        if desire == 'Least Free':
            self.__show_least_free()
        elif desire == 'Hint':
            self.__show_hint()
        elif desire == '# Solutions':
            self.__show_solution_count()
        elif desire == 'Freedom':
            self.__show_freedom()
        elif desire == 'Difficulty':
            self.__show_difficulty()
        elif desire == 'Sofa':
            self.__show_sofa()
        elif desire == 'Sanity Check':
            self.__sanity_check()
        else:
            pass



    def __dispatch_clear_choice(self, *args): # pylint: disable=W0613
        desire = self.clear_var.get()
        if desire == 'Puzzle':
            self.__clear_puzzle()
        elif desire == 'Solution':
            self.__clear_solution()
        else:
            pass


    def __draw_grid(self):
        """Draws grid divided with blue lines into 3x3 squares."""
        for i in range(10):
            color = 'blue' if i % 3 == 0 else 'gray'

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)


    def __draw_free(self, row, col, free):
        x = MARGIN + col * SIDE
        y = MARGIN + row * SIDE
        for val in free:
            dloc = DELTA[val]
            self.canvas.create_text(x + dloc[0], y + dloc[1], text=str(val), tags='free', fill='red', font=SudokuUI.free_font)


    def __draw_puzzle(self, freedom=None):
        self.canvas.delete('numbers')
        self.canvas.delete('free')
        for row in range(9):
            for col in range(9):
                answer = self.game.puzzle.get_cell(row, col)
                if answer is not None:
                    x = MARGIN + col * SIDE + SIDE / 2
                    y = MARGIN + row * SIDE + SIDE / 2
                    original = self.game.start_puzzle.get_cell(row, col)
                    color = 'black' if answer == original else 'sea green'
                    self.canvas.create_text(x, y, text=answer, tags='numbers', fill=color, font=SudokuUI.font)
                elif self.game.solution is not None:
                    solution = self.game.solution.get_cell(row, col)
                    if solution is not None:
                        x = MARGIN + col * SIDE + SIDE / 2
                        y = MARGIN + row * SIDE + SIDE / 2
                        self.canvas.create_text(x, y, text=solution, tags='numbers', fill='purple', font=SudokuUI.font)
                else:
                    if freedom is not None:
                        self.__draw_free(row, col, freedom.freedom_set(row, col))

    def __draw_cursor(self):
        self.canvas.delete('cursor')
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline='red', tags='cursor'
            )
            self.game.cell_selected(self.row, self.col)

    def __draw_message(self, tag, textstr, fillc, outlinec):
        # create a oval (which will be a circle)
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags=tag, fill=fillc, outline=outlinec
        )
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(x, y, text=textstr, tags=tag, fill='white', font=SudokuUI.font)

    def __draw_victory(self):
        self.__draw_message('victory', 'You win!', 'dark orange', 'orange')

    def __draw_no_solution(self): # pylint: disable=R0201
        messagebox.showinfo('Bummer', 'No Solution!')

    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) // SIDE, (x - MARGIN) // SIDE

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            #iam: the elif choice makes an original entry permanent.
            elif self.game.start_puzzle.get_cell(row, col) is not None:
                return
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row < 0 or self.col < 0:
            return
        if event.keysym == "BackSpace":
            self.game.puzzle.erase_cell(self.row, self.col)
        elif event.char in '1234567890':
            val = int(event.char)
            if val == 0:
                self.game.puzzle.erase_cell(self.row, self.col)
            else:
                self.game.puzzle.set_cell(self.row, self.col, val)
        else:
            return
        self.col, self.row = -1, -1
        self.__draw_puzzle()
        self.__draw_cursor()
        if self.game.check_win():
            self.__draw_victory()

    def __clear_messages(self):
        for tag in ['victory', 'failure', 'count']:
            self.canvas.delete(tag)
        self.message_text.set('')

    def __new_puzzle(self):
        self.__clear_messages()
        difficulty, target, empty_cells = self.game.new()
        self.message_text.set(f'Difficulty: {difficulty} Target: {target} Empty: {empty_cells}')
        self.__draw_puzzle()

    def __clear_puzzle(self):
        self.game.start()
        self.__clear_messages()
        self.__draw_puzzle()

    def __clear_solution(self):
        self.__clear_messages()
        self.game.clear_solution()
        self.__draw_puzzle()

    def __solve_puzzle(self):
        if not self.game.solve():
            self.__draw_no_solution()
        self.__draw_puzzle()

    def __show_solution_count(self):
        count = self.game.count_solutions()
        if count == 0:
            text = 'There are no solutions.'
        elif count == 1:
            text = 'There is a unique solution.'
        elif count < ALEPH_NOUGHT:
            text = f'There are {count} solutions'
        else:
            text = f'There are >= {ALEPH_NOUGHT} solutions'
        self.message_text.set(text)

    def __show_least_free(self):
        cell = self.game.least_free()
        text = f'A least free cell is: {cell}'
        self.message_text.set(text)
        if cell is not None:
            self.row, self.col = cell
            self.__draw_cursor()

    def __show_hint(self):
        success, hint = self.game.get_hint()
        if success is None:
            messagebox.showinfo('Sorry', hint)
            return
        (i, j, val, count) = success
        self.row = i
        self.col = j
        self.__draw_cursor()
        if DEBUG:
            print(f'The cell [{i}, {j}] should contain {val}')
        messagebox.showinfo(f'A Hint: {count} rules are needed', hint)

    def __show_freedom(self):
        self.__draw_puzzle(self.game.puzzle.freedom)


    def __show_sofa(self):
        self.game.puzzle.dump_value_map()
        self.game.puzzle.freedom.dump_sofa()

    def __sanity_check(self):
        self.game.sanity_check()


    def __show_difficulty(self):
        diff = self.game.get_difficulty()
        empty_cells = self.game.get_empty_cell_count()
        if diff < 0:
            self.message_text.set('The puzzle has no solution.')
        else:
            self.message_text.set(f'The current difficulty metric is: {diff} and {empty_cells} empty cells remaining.')

    def __check_puzzle(self):
        status = self.game.check()
        if status:
            empty_cells = self.game.get_empty_cell_count()
            self.message_text.set(f'Everything seems OK, there are {empty_cells} left.')
        else:
            self.message_text.set('Something is wrong!')
