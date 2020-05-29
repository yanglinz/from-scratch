import subprocess

from lark import Lark

parser_grammar = r"""
start: command_line

command_line: command | pipeline
pipeline: command SPACE PIPE SPACE command_line
command: COMMAND(SPACE COMMAND)*

SPACE: " "+
PIPE: "|"
COMMAND: /[^\s|]+/
"""

parser = Lark(parser_grammar)


class Command:
    def __init__(self, parsed_tree):
        args = parsed_tree.children
        args = [a for a in args if a.type != "SPACE"]
        self.args = args

    def execute(self):
        proc_args = [a.value.strip("'") for a in self.args]
        subprocess.call(proc_args)


class Pipeline:
    def __init__(self, parsed_tree):
        pass

    def execute(self):
        pass


def main():
    while True:
        user_input = input("> ")
        parsed_input = parser.parse(user_input)
        cmd = Command(parsed_input)
        cmd.execute()


if __name__ == "__main__":
    main()
