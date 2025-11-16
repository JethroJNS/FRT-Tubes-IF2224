import re
from src.tokens import (
    Token, TokenType, KEYWORDS,
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
        if ch == "{":
            start_col = col
            end_idx = source_code.find("}", i + 1)
            if end_idx == -1:
                print(f"Warning: Unclosed comment at line {line}")
                break
            # Hitung newlines dalam komentar
            comment_content = source_code[i:end_idx + 1]
            newline_count = comment_content.count('\n')
            if newline_count > 0:
                line += newline_count
                last_newline_pos = comment_content.rfind('\n')
                col = len(comment_content) - last_newline_pos
            else:
                col += len(comment_content)
            i = end_idx + 1
            continue

        # Skip komentar dengan tanda kurung bintang (* ... *)
        if i + 1 < length and source_code[i:i+2] == "(*":
            start_col = col
            end_idx = source_code.find("*)", i + 2)
            if end_idx == -1:
                print(f"Warning: Unclosed comment at line {line}")
                break
            # Hitung newlines dalam komentar
            comment_content = source_code[i:end_idx + 2]
            newline_count = comment_content.count('\n')
            if newline_count > 0:
                line += newline_count
                last_newline_pos = comment_content.rfind('\n')
                col = len(comment_content) - last_newline_pos
            else:
                col += len(comment_content)
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
            else:
                # Jika tidak dikenali, treat as unknown
                tokens.append(Token(TokenType.UNKNOWN, matched, line, col))
            i += len(matched)
            col += len(matched)
            continue

        # String
        if ch == "'":
            start_col = col
            j = i + 1
            while j < length:
                if source_code[j] == "'":
                    # Cek jika ini escaped quote ('')
                    if j + 1 < length and source_code[j + 1] == "'":
                        j += 2
                    else:
                        break
                elif source_code[j] == "\n":
                    break  # String literal tidak boleh ada newline
                else:
                    j += 1
            
            if j >= length or source_code[j] != "'":
                print(f"Warning: Unterminated string at line {line}")
                break
                
            literal = source_code[i:j + 1]
            tokens.append(Token(TokenType.STRING_LITERAL, literal, line, start_col))
            i = j + 1
            col += len(literal)
            continue

        # Identifier atau Keyword
        if ch.isalpha() or ch == '_':
            start = i
            while i < length and (source_code[i].isalnum() or source_code[i] == '_'):
                i += 1
            lexeme = source_code[start:i]
            
            token_type = classify_word_or_operator_word(lexeme)
            tokens.append(Token(token_type, lexeme, line, col))
            col += len(lexeme)
            continue

        # Angka
        if ch.isdigit():
            start = i
            # Baca semua digit sampai non-digit
            while i < length and source_code[i].isdigit():
                i += 1
            
            # Cek jika ada decimal point
            if i < length and source_code[i] == '.':
                # Cek karakter setelah dot
                if i + 1 < length and source_code[i + 1].isdigit():
                    # Ini number real, include the dot
                    i += 1  # include the dot
                    while i < length and source_code[i].isdigit():
                        i += 1
                else:
                    # Ini bukan number real, hanya ambil digitnya saja
                    pass
                    
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