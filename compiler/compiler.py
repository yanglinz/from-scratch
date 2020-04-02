from dataclasses import dataclass
import pathlib
import pprint
import re


class TokenMatchException(Exception):
    pass


class TokenTypes:
    define = ":define"
    end = ":end"
    identifier = ":identifier"
    integer = ":integer"
    open_paren = ":open_paren"
    close_paren = ":close_paren"


@dataclass
class Token:
    token_type: str
    value: str


class Tokenizer:
    TOKEN_TYPES = [
        (TokenTypes.define, "def"),
        (TokenTypes.end, "end"),
        (TokenTypes.identifier, "[a-zA-Z]+"),
        (TokenTypes.integer, "[0-9]+"),
        (TokenTypes.open_paren, "\("),
        (TokenTypes.close_paren, "\)"),
    ]

    def __init__(self, code):
        self.code = code.strip()

    def _tokenize_next(self, code):
        for token_type, token_re in self.TOKEN_TYPES:
            # TODO: Come up with a better way to join regex
            grouped_token_re = f"\\A(\\b{token_re}\\b)"
            if token_type == TokenTypes.open_paren or TokenTypes.close_paren:
                grouped_token_re = f"\\A({token_re})"

            matched = re.search(grouped_token_re, code)
            if matched:
                value = matched.group(0)
                position = matched.end(0)
                return Token(token_type=token_type, value=value), position

        raise TokenMatchException

    def tokenize(self):
        tokenized = []

        code = self.code
        while code:
            token, position = self._tokenize_next(code)
            tokenized.append(token)
            code = code[position:]
            code = code.lstrip()

        pprint.pprint(tokenized)


def main():
    src_path = pathlib.Path(__file__).parent / "test.src"
    with open(src_path) as source:
        content = source.read()

    Tokenizer(content).tokenize()


if __name__ == "__main__":
    main()
