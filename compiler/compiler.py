import pathlib


class Tokenizer:
    def __init__(self, code):
        self.code = code

    def tokenize(self):
        print(self.code)
        pass


def main():
    src_path = pathlib.Path(__file__).parent / "test.src"
    with open(src_path) as source:
        content = source.read()

    Tokenizer(content).tokenize()


if __name__ == "__main__":
    main()
