import subprocess

from lark import Lark

parser_grammar = r"""
start: COMMAND(SPACE COMMAND)*

COMMAND: /[^\s]+/

SPACE: " "+
"""

parser = Lark(parser_grammar)


class Command:
    def __init__(self, parsed_tree):
        args = parsed_tree.children
        args = [a for a in args if a.type != "SPACE"]
        self.args = args

    def execute(self):
        proc_args = [a.value for a in self.args]
        subprocess.call(proc_args)


class Shell:
    pass


def main():
    while True:
        user_input = input("> ")
        parsed_input = parser.parse(user_input)
        cmd = Command(parsed_input)
        cmd.execute()


if __name__ == "__main__":
    main()
