import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.lexer import tokenize
from src.parser import Parser
from src.parse_tree import print_tree, ParseNode
from src.reader import Reader
from src.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from src.semantic_analyzer.ast_printer import print_decorated_ast, print_symbol_tables

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m src.compiler <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print("=== TOKENS ===")
    tokens = tokenize(source_code)
    
    # Print tokens with numbering
    for i, token in enumerate(tokens):
        print(f"{i:3}: {token.type.name:20} '{token.value}' at {token.line}:{token.column}")
    
    print("==============")
    print()
    
    # Parse
    try:
        parser = Parser(tokens)
        parse_tree = parser.parse()
        
        print("=== PARSE TREE ===")
        print_tree(parse_tree)
        print()
        
        # Debug: print assignment structure
        # print("\n=== DEBUG ASSIGNMENT STRUCTURE ===")
        # def debug_assignments(node: ParseNode, level: int = 0):
        #     if node.name == "<assignment-statement>":
        #         indent = "  " * level
        #         print(f"{indent}ASSIGNMENT FOUND:")
        #         print(f"{indent}  Children: {[child.name for child in node.children]}")
        #         for i, child in enumerate(node.children):
        #             token_info = f" - '{child.token.value}'" if child.token else ""
        #             print(f"{indent}    {i}: {child.name}{token_info}")
        #     for child in node.children:
        #         debug_assignments(child, level + 1)
        
        # debug_assignments(parse_tree)
        # print()
        
        # Semantic Analysis
        print("=== SEMANTIC ANALYSIS ===")
        analyzer = SemanticAnalyzer()
        ast = analyzer.analyze(parse_tree)
        
        print("\n=== DECORATED AST ===")
        print_decorated_ast(ast)
        
        print_symbol_tables(analyzer)
        
        if analyzer.errors:
            print(f"\n✗ Found {len(analyzer.errors)} semantic errors:")
            for error in analyzer.errors:
                print(f"  - {error}")
        else:
            print(f"\n✓ No semantic errors found")
            
    except Exception as e:
        print(f"Error during parsing or semantic analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()