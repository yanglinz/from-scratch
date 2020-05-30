from lark import Lark

parser_grammar = r"""
start: PIPE+

PIPE: "|"
"""

parser = Lark(parser_grammar)


class Shell:
    pass


def main():
    user_input = input("> ")
    print(user_input)


if __name__ == "__main__":
    # main()
    parsed = parser.parse("|||")
    print(parsed)
