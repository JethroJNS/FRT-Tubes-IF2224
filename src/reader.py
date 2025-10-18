from src.tokens import Token

class Reader:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def read(self):
        for tok in self.tokens:
            print(f"{tok.type.name}({tok.value})")
