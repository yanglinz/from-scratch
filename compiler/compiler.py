from dataclasses import dataclass
import pathlib
import pprint
import re
import typing


class LexerTokenMatchException(Exception):
    pass


class ParserUnexpectedTokenException(Exception):
    pass


class GeneratorUnexpectedNodeException(Exception):
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


@dataclass
class ASTNodeFunctionCall:
    name: str
    arg_expressions: typing.Any


@dataclass
class ASTNodeVarRef:
    value: str


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

        raise LexerTokenMatchException({"code": code})

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

        raise ParserUnexpectedTokenException(
            {"expected": expected_type, "received": token}
        )

    def _peek(self, expected_type, offset=0):
        return self.token_list[offset].token_type == expected_type

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

    def _parse_arg_expressions(self):
        arg_expressions = []

        self._consume(TokenTypes.open_paren)
        if not self._peek(TokenTypes.close_paren):
            arg_expression = self._parse_expression()
            arg_expressions.append(arg_expression)

            while self._peek(TokenTypes.comma):
                self._consume(TokenTypes.comma)
                arg_expression = self._parse_expression()
                arg_expressions.append(arg_expression)

        self._consume(TokenTypes.close_paren)
        return arg_expressions

    def _parse_func_call(self):
        name = self._consume(TokenTypes.identifier).value
        arg_expressions = self._parse_arg_expressions()
        return ASTNodeFunctionCall(name=name, arg_expressions=arg_expressions)

    def _parse_var_ref(self):
        var_name = self._consume(TokenTypes.identifier).value
        return ASTNodeVarRef(value=var_name)

    def _parse_expression(self):
        if self._peek(TokenTypes.integer):
            return self._parse_integer()
        elif self._peek(TokenTypes.identifier) and self._peek(
            TokenTypes.open_paren, offset=1
        ):
            return self._parse_func_call()

        return self._parse_var_ref()

    def _parse_def(self):
        self._consume(TokenTypes.define)
        name = self._consume(TokenTypes.identifier).value
        arg_names = self._parse_def_arg_names()
        body = self._parse_expression()
        self._consume(TokenTypes.end)
        return ASTNodeDefine(name=name, arg_names=arg_names, body=body)

    def parse(self):
        return self._parse_def()


class Generator:
    def generate(self, node):
        raise GeneratorUnexpectedNodeException({"node": node})


def main():
    src_path = pathlib.Path(__file__).parent / "test.src"
    with open(src_path) as source:
        content = source.read()

    tokens = Tokenizer(content).tokenize()
    print("Tokens:")
    pprint.pprint(tokens)
    print("\n")

    tree = Parser(tokens).parse()
    print("Parsed Tree:")
    pprint.pprint(tree)
    print("\n")

    code = Generator().generate(tree)
    print("Generated Code:")
    pprint.pprint(code)


if __name__ == "__main__":
    main()
