from dataclasses import dataclass
import pathlib
import pprint
import re
import typing


class LexingTokenMatchException(Exception):
    pass


class ParsingUnexpectedTokenException(Exception):
    pass


class TokenTypes:
    define = ":define"
    end = ":end"
    identifier = ":identifier"
    integer = ":integer"
    open_paren = ":open_paren"
    close_paren = ":close_paren"
    comma = ":comma"


@dataclass
class Token:
    token_type: str
    value: str


@dataclass
class ASTNodeDefine:
    name: str
    arg_names: typing.List[str]
    body: typing.Any


@dataclass
class ASTNodeInteger:
    value: int


class Tokenizer:
    TOKEN_TYPES = [
        (TokenTypes.define, "def"),
        (TokenTypes.end, "end"),
        (TokenTypes.identifier, "[a-zA-Z]+"),
        (TokenTypes.integer, "[0-9]+"),
        (TokenTypes.open_paren, "\("),
        (TokenTypes.close_paren, "\)"),
        (TokenTypes.comma, ","),
    ]

    def __init__(self, code):
        self.code = code.strip()

    def _tokenize_next(self, code):
        for token_type, token_re in self.TOKEN_TYPES:
            # TODO: Come up with a better way to join regex
            grouped_token_re = f"\\A(\\b{token_re}\\b)"
            if token_type in (
                TokenTypes.open_paren,
                TokenTypes.close_paren,
                TokenTypes.comma,
            ):
                grouped_token_re = f"\\A({token_re})"

            matched = re.search(grouped_token_re, code)
            if matched:
                value = matched.group(0)
                position = matched.end(0)
                return Token(token_type=token_type, value=value), position

        raise LexingTokenMatchException({"code": code})

    def tokenize(self):
        token_list = []

        code = self.code
        while code:
            token, position = self._tokenize_next(code)
            token_list.append(token)
            code = code[position:]
            code = code.lstrip()

        return token_list


class Parser:
    def __init__(self, token_list):
        self.token_list = token_list

    def _consume(self, expected_type):
        token = self.token_list[0]
        self.token_list = self.token_list[1:]

        if token.token_type == expected_type:
            return token

        raise ParsingUnexpectedTokenException(
            {"expected": expected_type, "received": token}
        )

    def _peek(self, expected_type):
        return self.token_list[0].token_type == expected_type

    def _parse_def_arg_names(self):
        arg_names = []
        self._consume(TokenTypes.open_paren)

        if self._peek(TokenTypes.identifier):
            arg_token = self._consume(TokenTypes.identifier)
            arg_names.append(arg_token.value)

            while self._peek(TokenTypes.comma):
                self._consume(TokenTypes.comma)
                arg_token = self._consume(TokenTypes.identifier)
                arg_names.append(arg_token.value)

        self._consume(TokenTypes.close_paren)
        return arg_names

    def _parse_integer(self):
        token = self._consume(TokenTypes.integer)
        return ASTNodeInteger(value=int(token.value))

    def _parse_expression(self):
        return self._parse_integer()

    def _parse_def(self):
        self._consume(TokenTypes.define)
        name = self._consume(TokenTypes.identifier).value
        arg_names = self._parse_def_arg_names()
        body = self._parse_expression()
        self._consume(TokenTypes.end)
        return ASTNodeDefine(name=name, arg_names=arg_names, body=body)

    def parse(self):
        return self._parse_def()


def main():
    src_path = pathlib.Path(__file__).parent / "test.src"
    with open(src_path) as source:
        content = source.read()

    tokens = Tokenizer(content).tokenize()
    print("\nTokens:")
    pprint.pprint(tokens)

    parsed = Parser(tokens).parse()
    print("\nParsed Tree:")
    pprint.pprint(parsed)


if __name__ == "__main__":
    main()
