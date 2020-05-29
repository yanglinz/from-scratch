import re
import sys
import tty
import termios
from contextlib import contextmanager


@contextmanager
def raw_mode():
    fd = sys.stdin.fileno()
    current = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, current)


class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def insert(self, char, row, col):
        new_lines = self.lines
        new_lines[row] = new_lines[row][:col] + char + new_lines[row][col:]
        return Buffer(new_lines)

    def render(self):
        for l in self.lines:
            print(l, end="\r\n")


class Cursor:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def _clamp(self, c, buffer):
        def clamp_helper(n, minimum_n, maximum_n):
            return max(min(n, maximum_n), minimum_n)

        c.row = clamp_helper(c.row, 0, len(buffer.lines) - 1)
        current_line = buffer.lines[c.row]
        c.col = clamp_helper(c.col, 0, len(current_line))
        return c

    def up(self, buffer):
        return self._clamp(Cursor(self.row - 1, self.col), buffer)

    def down(self, buffer):
        return self._clamp(Cursor(self.row + 1, self.col), buffer)

    def left(self, buffer):
        return self._clamp(Cursor(self.row, self.col - 1), buffer)

    def right(self, buffer):
        return self._clamp(Cursor(self.row, self.col + 1), buffer)


class ANSI:
    @classmethod
    def clear_screen(cls):
        print(chr(27) + "[2J")

    @classmethod
    def move_cursor(cls, row, col):
        print(chr(27) + f"[{row + 1};{col + 1}H")


class Editor:
    def __init__(self, filename):
        with open(filename) as f:
            lines = f.readlines()
        lines = [re.sub(r"\n$", "", l) for l in lines]

        self.buffer = Buffer(lines)
        self.cursor = Cursor(0, 0)

    def render(self):
        ANSI.clear_screen()
        ANSI.move_cursor(0, 0)
        self.buffer.render()
        ANSI.move_cursor(self.cursor.row, self.cursor.col)

    def handle_input(self):
        class Char:
            ESC = 3
            ARROW_UP = 65
            ARROW_DOWN = 66
            ARROW_LEFT = 68
            ARROW_RIGHT = 67

        char = sys.stdin.read(1)
        char_ord = ord(char)

        if char_ord == Char.ESC:
            sys.exit(0)
        elif char_ord == Char.ARROW_UP:
            self.cursor = self.cursor.up(self.buffer)
        elif char_ord == Char.ARROW_DOWN:
            self.cursor = self.cursor.down(self.buffer)
        elif char_ord == Char.ARROW_LEFT:
            self.cursor = self.cursor.left(self.buffer)
        elif char_ord == Char.ARROW_RIGHT:
            self.cursor = self.cursor.right(self.buffer)
        elif char:
            self.buffer = self.buffer.insert(char, self.cursor.row, self.cursor.col)

        # Debugging statement
        # print(char_ord, end="\r\n")

    def run(self):
        with raw_mode():
            while True:
                self.render()
                self.handle_input()


if __name__ == "__main__":
    editor = Editor("text_editor/test.txt")
    editor.run()
