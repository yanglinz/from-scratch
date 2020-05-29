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

    def render(self):
        for l in self.lines:
            print(l, end="\r\n")


class Cursor:
    def __init__(self, row, col):
        self.row = row
        self.col = col


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
        ANSI.move_cursor(self.cursor.row, self.cursor.col)
        self.buffer.render()
        

    def handle_input(self):
        char = sys.stdin.read(1)
        if ord(char) == 3:
            sys.exit(0)

        print(ord(char), end="\r\n")

    def run(self):
        with raw_mode():
            while True:
                self.render()
                self.handle_input()


if __name__ == "__main__":
    editor = Editor("text_editor/test.txt")
    editor.run()
