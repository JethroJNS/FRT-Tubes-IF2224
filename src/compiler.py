import sys
from pathlib import Path
from src.lexer import tokenize
from src.reader import Reader

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py [program.pas]")
        sys.exit(1)

    pascal_file = sys.argv[1]
    if not Path(pascal_file).exists():
        print(f"Error: file '{pascal_file}' not found")
        sys.exit(1)

    with open(pascal_file, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    reader = Reader(tokens)
    reader.read()

if __name__ == "__main__":
    main()
