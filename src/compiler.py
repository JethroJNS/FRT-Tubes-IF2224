import sys
from pathlib import Path
from src.lexer import tokenize
from src.parser import Parser
from src.parse_tree import print_tree

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
    
    print("=== TOKENS ===")
    for i, token in enumerate(tokens):
        print(f"{i:3}: {token.type.name:20} '{token.value}' at {token.line}:{token.column}")
    print("==============")
    
    parser = Parser(tokens)
    try:
        root = parser.parse()
        print_tree(root)
    except Exception as e:
        print(f"Syntax error: {e}")

if __name__ == "__main__":
    main()