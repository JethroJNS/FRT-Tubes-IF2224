import re
from src.tokens import (
    Token, TokenType,
    classify_word_or_operator_word, classify_punct_or_ops,
    LONGEST_FIRST
)

def tokenize(source_code: str):
    tokens = []
    i = 0
    line, col = 1, 1
    length = len(source_code)

    while i < length:
        ch = source_code[i]

        # Skip whitespace
        if ch.isspace():
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1
            continue

        # Skip komentar dengan tanda kurung kurawal { ... }
        if ch == "{" and "}" in source_code[i:]:
            end_idx = source_code.find("}", i + 1)
            if end_idx == -1:
                print(f"Warning: Unclosed comment at line {line}")
                break
            i = end_idx + 1
            continue

        # Skip komentar dengan tanda kurung bintang (* ... *)
        if source_code.startswith("(*", i):
            end_idx = source_code.find("*)", i + 2)
            if end_idx == -1:
                print(f"Warning: Unclosed comment at line {line}")
                break
            i = end_idx + 2
            continue

        # Cek token multi-karakter
        matched = None
        for sym in LONGEST_FIRST:
            if source_code.startswith(sym, i):
                matched = sym
                break

        if matched:
            token_type = classify_punct_or_ops(matched)
            if token_type:
                tokens.append(Token(token_type, matched, line, col))
            i += len(matched)
            col += len(matched)
            continue

        # String
        if ch == "'":
            end_idx = i + 1
            while end_idx < length and source_code[end_idx] != "'":
                if source_code[end_idx] == "\n":
                    line += 1
                    col = 1
                end_idx += 1
            if end_idx >= length:
                print(f"Warning: Unterminated string at line {line}")
                break
            literal = source_code[i:end_idx + 1]
            tokens.append(Token(TokenType.STRING_LITERAL, literal, line, col))
            i = end_idx + 1
            col += len(literal)
            continue

        # Keyword
        if ch.isalpha():
            start = i
            while i < length and (source_code[i].isalnum() or source_code[i] == "_"):
                i += 1
            lexeme = source_code[start:i]
            token_type = classify_word_or_operator_word(lexeme)
            tokens.append(Token(token_type, lexeme, line, col))
            col += len(lexeme)
            continue

        # Angka
        if ch.isdigit():
            start = i
            has_dot = False
            while i < length and (source_code[i].isdigit() or source_code[i] == "."):
                if source_code[i] == ".":
                    if has_dot:
                        break
                    has_dot = True
                i += 1
            lexeme = source_code[start:i]
            tokens.append(Token(TokenType.NUMBER, lexeme, line, col))
            col += len(lexeme)
            continue

        # Operator dan tanda baca
        token_type = classify_punct_or_ops(ch)
        if token_type:
            tokens.append(Token(token_type, ch, line, col))
            i += 1
            col += 1
            continue

        # Simbol unknown
        tokens.append(Token(TokenType.UNKNOWN, ch, line, col))
        print(f"Unknown token '{ch}' at line {line}, column {col}")
        i += 1
        col += 1

    return tokens
