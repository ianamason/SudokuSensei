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

from tkinter import Canvas, Frame, Button, BOTH, TOP, LEFT

from Constants import WIDTH, HEIGHT, MARGIN, SIDE, PAD, ALEPH_NOUGHT

class SudokuUI(Frame): # pylint: disable=R0901
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1

        self.__init_ui()

    def __init_ui(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)

        clear_puzzle_button = Button(self,
                                     text="Clear Puzzle",
                                     command=self.__clear_puzzle)
        clear_puzzle_button.pack(side=LEFT, padx=PAD)

        clear_solution_button = Button(self,
                                       text="Clear Solution",
                                       command=self.__clear_solution)
        clear_solution_button.pack(side=LEFT, padx=PAD)

        solve_button = Button(self,
                              text="Solve",
                              command=self.__solve_puzzle)
        solve_button.pack(side=LEFT, padx=PAD)

        count_button = Button(self,
                              text="Count Solutions",
                              command=self.__count_solutions)
        count_button.pack(side=LEFT, padx=PAD)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

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

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "sea green"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )
                elif self.game.solution is not None:
                    solution = self.game.solution[i][j]
                    if solution != 0:
                        x = MARGIN + j * SIDE + SIDE / 2
                        y = MARGIN + i * SIDE + SIDE / 2
                        self.canvas.create_text(
                            x, y, text=solution, tags="numbers", fill="purple"
                        )


    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

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
        self.canvas.create_text(
            x, y,
            text=textstr, tags=tag,
            fill="white", font=("Arial", 32)
        )


    def __draw_victory(self):
        self.__draw_message("victory", "You win!", "dark orange", "orange")


    def __draw_no_solution(self):
        self.__draw_message("failure", "No Solution!", "dark red", "red")

    def __draw_solution_count(self):
        count = self.game.count_solutions()
        if count == 0:
            text = "No solutions."
        elif count == 1:
            text = "Unique solution."
        elif count < ALEPH_NOUGHT:
            text = "{0} solutions".format(count)
        else:
            text = ">= {0} solutions".format(count)

        self.__draw_message("count", text, "dark green", "green")


    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates (iam 06/03/2020: which are now floats so need to be rounded down)
            row, col = (y - MARGIN) // SIDE, (x - MARGIN) // SIDE

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            #iam: the elif choice makes an entry permanent, not sure why Lynn Root chose that route.
            #elif self.game.puzzle[row][col] == 0:
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()

    def __clear_messages(self):
        for tag in ["victory", "failure", "count"]:
            self.canvas.delete(tag)

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

    def __count_solutions(self):
        self.__draw_solution_count()
        self.__draw_puzzle()
