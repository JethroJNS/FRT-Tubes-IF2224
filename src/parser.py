from __future__ import annotations
from typing import List, Optional

from src.tokens import Token, TokenType
from src.parse_tree import ParseNode

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def debug_context(self, message: str = ""):
        if message:
            print(f"DEBUG: {message}")
        if self.current():
            print(f"Current: {self.current().type.name}('{self.current().value}') at {self.current().line}:{self.current().column}")
        else:
            print("Current: EOF")
        print("Next tokens:")
        for i in range(self.pos, min(self.pos + 5, len(self.tokens))):
            tok = self.tokens[i]
            marker = ">>>" if i == self.pos else "   "
            print(f"{marker} {i}: {tok.type.name:20} '{tok.value}'")
        print("---")

    # ============== Utility Function ==============
    def current(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def lookahead(self, offset: int = 1) -> Optional[Token]:
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def advance(self) -> Optional[Token]:
        tok = self.current()
        if tok is not None:
            self.pos += 1
        return tok

    def at_end(self) -> bool:
        return self.current() is None

    def match(self, *types: TokenType) -> Optional[Token]:
        tok = self.current()
        if tok is not None and tok.type in types:
            self.pos += 1
            return tok
        return None

    def expect(self, expected_type: TokenType) -> Token:
        tok = self.current()
        if tok is None:
            raise ParserError(f"Expected {expected_type.name}, but found EOF")
        if tok.type != expected_type:
            raise ParserError(
                f"Expected {expected_type.name}, but found {tok.type.name} "
                f"at line {tok.line}, column {tok.column}"
            )
        self.pos += 1
        return tok

    # ============== helper untuk keyword & operator spesifik ==============

    def check_keyword(self, word: str) -> bool:
        tok = self.current()
        return (
            tok is not None
            and tok.type == TokenType.KEYWORD
            and str(tok.value).lower() == word
        )

    # Keyword
    def expect_keyword(self, word: str) -> Token:
        tok = self.current()
        if not self.check_keyword(word):
            raise ParserError(
                f"Expected KEYWORD({word}), but found "
                f"{tok.type.name if tok else 'EOF'}({tok.value if tok else ''})"
            )
        self.pos += 1
        return tok

    # Relational Operator
    def expect_relop(self, symbol: str) -> Token:
        tok = self.current()
        if (
            tok is None
            or tok.type != TokenType.RELATIONAL_OPERATOR
            or str(tok.value) != symbol
        ):
            raise ParserError(
                f"Expected RELATIONAL_OPERATOR({symbol}), but found "
                f"{tok.type.name if tok else 'EOF'}({tok.value if tok else ''})"
            )
        self.pos += 1
        return tok

    # ============== Entry Point ==============
    # Keterangan
    # ::=   : definisi
    # |     : alternatif
    # { X } : pengulangan 0 atau lebih kali
    # [ X ] : opsional (0 atau 1 kali)
    def parse(self) -> ParseNode:
        # <program> ::= <program-header> <declaration-part> <compound-statement> DOT
        root = self.parse_program()

        # kalau setelah parse masih ada token tersisa => error.
        if not self.at_end():
            tok = self.current()
            raise ParserError(
                f"Unexpected token {tok.type.name}({tok.value}) "
                f"at line {tok.line}, column {tok.column}"
            )

        return root

    # ============== 1. Program ==============

    def parse_program(self) -> ParseNode:
        # <program> ::= <program-header> <declaration-part> <compound-statement> DOT
        node = ParseNode("<program>")

        node.children.append(self.parse_program_header()) # <program-header>
        node.children.append(self.parse_declaration_part()) # <declaration-part>
        node.children.append(self.parse_compound_statement()) # <compound-statement>

        dot_tok = self.expect(TokenType.DOT)
        node.children.append(ParseNode("DOT", token=dot_tok)) # DOT

        return node

    def parse_program_header(self) -> ParseNode:
        # <program-header> ::= KEYWORD(program) IDENTIFIER SEMICOLON
        node = ParseNode("<program-header>")

        kw_prog = self.expect_keyword("program")
        node.children.append(ParseNode("KEYWORD(program)", token=kw_prog))

        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        semi = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi))

        return node

    # ============== 2. Deklarasi ==============

    def parse_declaration_part(self) -> ParseNode:
        # <declaration-part> ::=
        #     { <const-declaration> }
        #     { <type-declaration> }
        #     { <var-declaration> }
        #     { <subprogram-declaration> }

        node = ParseNode("<declaration-part>")

        # { <const-declaration> }
        while self.check_keyword("konstanta"):
            node.children.append(self.parse_const_declaration())

        # { <type-declaration> }
        while self.check_keyword("tipe"):
            node.children.append(self.parse_type_declaration())

        # { <var-declaration> }
        while self.check_keyword("variabel"):
            node.children.append(self.parse_var_declaration())

        # { <subprogram-declaration> }  prosedur / fungsi
        while self.check_keyword("prosedur") or self.check_keyword("fungsi"):
            node.children.append(self.parse_subprogram_declaration())

        return node

    # -------- 2.1 Deklarasi Konstanta --------

    def parse_const_declaration(self) -> ParseNode:
        # <const-declaration> ::= KEYWORD(konstanta) <const-item> { <const-item> }
        node = ParseNode("<const-declaration>")

        kw = self.expect_keyword("konstanta")
        node.children.append(ParseNode("KEYWORD(konstanta)", token=kw))

        # minimal satu <const-item>
        node.children.append(self.parse_const_item())

        # { <const-item> }
        while True: # selama token saat ini IDENTIFIER, masih dianggap const-item berikutnya
            tok = self.current()
            if tok is not None and tok.type == TokenType.IDENTIFIER:
                node.children.append(self.parse_const_item())
            else:
                break

        return node

    def parse_const_item(self) -> ParseNode:
        # <const-item> ::= IDENTIFIER '=' <const-value> SEMICOLON
        # di level token : '=' dihasilkan sebagai RELATIONAL_OPERATOR dengan value '='.
        node = ParseNode("<const-item>")

        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        eq = self.expect_relop("=")
        node.children.append(ParseNode("RELATIONAL_OPERATOR(=)", token=eq))

        node.children.append(self.parse_const_value())

        semi = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi))

        return node

    def parse_const_value(self) -> ParseNode:
        # <const-value> ::= NUMBER | CHAR_LITERAL | STRING_LITERAL
        node = ParseNode("<const-value>")
        tok = self.current()

        if tok is None:
            raise ParserError("Unexpected EOF in <const-value>")

        if tok.type == TokenType.NUMBER:
            node.children.append(ParseNode("NUMBER", token=self.advance()))
        elif tok.type == TokenType.CHAR_LITERAL:
            node.children.append(ParseNode("CHAR_LITERAL", token=self.advance()))
        elif tok.type == TokenType.STRING_LITERAL:
            node.children.append(ParseNode("STRING_LITERAL", token=self.advance()))
        elif tok.type == TokenType.IDENTIFIER:
            # Identifier juga bisa sebagai const value (untuk konstanta lain)
            node.children.append(ParseNode("IDENTIFIER", token=self.advance()))
        else:
            raise ParserError(
                f"Expected NUMBER / CHAR_LITERAL / STRING_LITERAL / IDENTIFIER in <const-value>, "
                f"found {tok.type.name}({tok.value})"
            )

        return node
    
    # -------- 2.2 Deklarasi Tipe --------

    def parse_type_declaration(self) -> ParseNode:
        # <type-declaration> ::= KEYWORD(tipe) <type-item> { <type-item> }
        node = ParseNode("<type-declaration>")
        kw = self.expect_keyword("tipe")
        node.children.append(ParseNode("KEYWORD(tipe)", token=kw))

        node.children.append(self.parse_type_item())
        while True:
            tok = self.current()
            if tok is not None and tok.type == TokenType.IDENTIFIER:
                node.children.append(self.parse_type_item())
            else:
                break

        return node

    def parse_type_item(self) -> ParseNode:
        # <type-item> ::= IDENTIFIER '=' <type-definition> SEMICOLON
        node = ParseNode("<type-item>")

        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        eq = self.expect_relop("=")
        node.children.append(ParseNode("RELATIONAL_OPERATOR(=)", token=eq))

        node.children.append(self.parse_type_definition())

        semi = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi))

        return node

    def parse_type_definition(self) -> ParseNode:
        # <type-definition> ::= <type> | <range>
        # Heuristik: jika di sisa token sebelum SEMICOLON/RBRACKET ada RANGE_OPERATOR, 
        # maka parse sebagai <range>,
        # selain itu sebagai <type>.
        node = ParseNode("<type-definition>")
        
        # Cek token saat ini untuk menentukan apakah ini range atau type biasa
        tok = self.current()
        
        # Jika token adalah NUMBER, pasti ini range
        if tok and tok.type == TokenType.NUMBER:
            node.children.append(self.parse_range())
            return node
        
        # Jika token adalah IDENTIFIER, cek apakah diikuti oleh RANGE_OPERATOR
        if tok and tok.type == TokenType.IDENTIFIER:
            # Look ahead untuk melihat apakah ini range atau type biasa
            if (self.lookahead(1) and 
                (self.lookahead(1).type == TokenType.RANGE_OPERATOR or
                (self.lookahead(1).type == TokenType.DOT and 
                self.lookahead(2) and self.lookahead(2).type == TokenType.DOT))):
                # Ini range dengan identifier
                node.children.append(self.parse_range())
                return node
        
        # Jika bukan range, parse sebagai type biasa
        node.children.append(self.parse_type())
        return node

    def parse_type(self) -> ParseNode:
        # <type> ::= KEYWORD(integer) | KEYWORD(real) | KEYWORD(boolean) | KEYWORD(char) | <array-type>
        node = ParseNode("<type>")

        if self.check_keyword("integer"):
            tok = self.expect_keyword("integer")
            node.children.append(ParseNode("KEYWORD(integer)", token=tok))
        elif self.check_keyword("real"):
            tok = self.expect_keyword("real")
            node.children.append(ParseNode("KEYWORD(real)", token=tok))
        elif self.check_keyword("boolean"):
            tok = self.expect_keyword("boolean")
            node.children.append(ParseNode("KEYWORD(boolean)", token=tok))
        elif self.check_keyword("char"):
            tok = self.expect_keyword("char")
            node.children.append(ParseNode("KEYWORD(char)", token=tok))
        elif self.check_keyword("string"):
            tok = self.expect_keyword("string")
            node.children.append(ParseNode("KEYWORD(string)", token=tok))
        elif self.check_keyword("rekaman"):
            node.children.append(self.parse_record_type())
        elif self.check_keyword("larik"):
            node.children.append(self.parse_array_type())
        else:
            # Bisa juga identifier (type alias)
            ident = self.expect(TokenType.IDENTIFIER)
            node.children.append(ParseNode("IDENTIFIER", token=ident))

        return node

    def parse_record_type(self) -> ParseNode:
        node = ParseNode("<record-type>")
        kw_rekaman = self.expect_keyword("rekaman")
        node.children.append(ParseNode("KEYWORD(rekaman)", token=kw_rekaman))

        node.children.append(self.parse_field_list())

        kw_selesai = self.expect_keyword("selesai")
        node.children.append(ParseNode("KEYWORD(selesai)", token=kw_selesai))
        return node

    def parse_field_list(self) -> ParseNode:
        node = ParseNode("<field-list>")
        while True:
            tok = self.current()
            if tok is None or self.check_keyword("selesai"):
                break
            if tok.type == TokenType.IDENTIFIER:
                node.children.append(self.parse_var_item())
            else:
                break
        return node

    def parse_array_type(self) -> ParseNode:
        node = ParseNode("<array-type>")
        kw_arr = self.expect_keyword("larik")
        node.children.append(ParseNode("KEYWORD(larik)", token=kw_arr))

        lbr = self.expect(TokenType.LBRACKET)
        node.children.append(ParseNode("LBRACKET", token=lbr))

        # Parse semua index specifications yang dipisahkan koma
        node.children.append(self.parse_index_specification())
        
        # Handle additional dimensions
        while self.current() and self.current().type == TokenType.COMMA:
            comma = self.expect(TokenType.COMMA)
            node.children.append(ParseNode("COMMA", token=comma))
            node.children.append(self.parse_index_specification())

        rbr = self.expect(TokenType.RBRACKET)
        node.children.append(ParseNode("RBRACKET", token=rbr))

        kw_dari = self.expect_keyword("dari")
        node.children.append(ParseNode("KEYWORD(dari)", token=kw_dari))

        node.children.append(self.parse_type())
        return node

    def parse_index_specification(self) -> ParseNode:
        node = ParseNode("<index-specification>")
        
        # Coba parse sebagai range dulu
        saved_pos = self.pos
        try:
            range_node = self.parse_range()
            node.children.append(range_node)
            return node
        except ParserError as e:
            # Jika bukan range, parse sebagai simple expression
            self.pos = saved_pos
            node.children.append(self.parse_simple_expression())
            return node

    def parse_range(self) -> ParseNode:
        node = ParseNode("<range>")
        
        # Parse first expression
        node.children.append(self.parse_simple_expression())

        # Handle berbagai kemungkinan range operator
        range_found = False
        
        # Cek RANGE_OPERATOR
        if self.current() and self.current().type == TokenType.RANGE_OPERATOR:
            rop = self.expect(TokenType.RANGE_OPERATOR)
            node.children.append(ParseNode("RANGE_OPERATOR", token=rop))
            range_found = True
        # Cek dua DOT berturut-turut  
        elif (self.current() and self.current().type == TokenType.DOT and
            self.lookahead(1) and self.lookahead(1).type == TokenType.DOT):
            dot1 = self.expect(TokenType.DOT)
            node.children.append(ParseNode("DOT", token=dot1))
            dot2 = self.expect(TokenType.DOT)
            node.children.append(ParseNode("DOT", token=dot2))
            range_found = True
        # Handle kasus dimana dot sudah termasuk dalam number (seperti "1.")
        elif (self.current() and self.current().type == TokenType.DOT and
            self.lookahead(1) and self.lookahead(1).type == TokenType.NUMBER):
            # Ini kasus khusus: number seperti "1." diikuti DOT dan number "10"
            dot = self.expect(TokenType.DOT)
            node.children.append(ParseNode("DOT", token=dot))
            # Anggap ini sebagai range operator
            range_found = True

        if not range_found:
            # Error handling yang lebih informatif
            current_token = self.current()
            if current_token:
                raise ParserError(
                    f"Expected range operator '..' after {node.children[0].children[0].token.value if node.children[0].children and node.children[0].children[0].token else 'expression'}, "
                    f"but found {current_token.type.name}('{current_token.value}') at line {current_token.line}"
                )
            else:
                raise ParserError("Expected range operator '..' but found EOF")

        # Parse second expression
        node.children.append(self.parse_simple_expression())
        return node

    # -------- 2.3 Deklarasi Variabel --------
    def parse_var_declaration(self) -> ParseNode:
        node = ParseNode("<var-declaration>")
        kw = self.expect_keyword("variabel")
        node.children.append(ParseNode("KEYWORD(variabel)", token=kw))

        node.children.append(self.parse_var_item())
        while True:
            tok = self.current()
            if tok is not None and tok.type == TokenType.IDENTIFIER:
                node.children.append(self.parse_var_item())
            else:
                break
        return node

    def parse_var_item(self) -> ParseNode:
        node = ParseNode("<var-item>")
        node.children.append(self.parse_identifier_list())

        colon = self.expect(TokenType.COLON)
        node.children.append(ParseNode("COLON", token=colon))

        node.children.append(self.parse_type())

        semi = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi))
        return node

    def parse_identifier_list(self) -> ParseNode:
        node = ParseNode("<identifier-list>")
        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        while True:
            if self.current() and self.current().type == TokenType.COMMA:
                comma = self.advance()
                node.children.append(ParseNode("COMMA", token=comma))
                ident2 = self.expect(TokenType.IDENTIFIER)
                node.children.append(ParseNode("IDENTIFIER", token=ident2))
            else:
                break
        return node

    # ========== 3. Subprogram ==========

    def parse_subprogram_declaration(self) -> ParseNode:
        # <subprogram-declaration> ::= <procedure-declaration> | <function-declaration>
        node = ParseNode("<subprogram-declaration>")

        if self.check_keyword("prosedur"):
            node.children.append(self.parse_procedure_declaration())
        elif self.check_keyword("fungsi"):
            node.children.append(self.parse_function_declaration())
        else:
            tok = self.current()
            raise ParserError(
                f"Expected KEYWORD(prosedur/fungsi) in <subprogram-declaration>, "
                f"found {tok.type.name if tok else 'EOF'}({tok.value if tok else ''})"
            )

        return node

    def parse_procedure_declaration(self) -> ParseNode:
        # <procedure-declaration> ::=
        #     KEYWORD(prosedur) IDENTIFIER
        #     [ <formal-parameter-list> ]
        #     SEMICOLON
        #     <block>
        #     SEMICOLON
        node = ParseNode("<procedure-declaration>")

        kw = self.expect_keyword("prosedur")
        node.children.append(ParseNode("KEYWORD(prosedur)", token=kw))

        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        if self.current() and self.current().type == TokenType.LPARENTHESIS:
            node.children.append(self.parse_formal_parameter_list())

        semi1 = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi1))

        node.children.append(self.parse_block())

        semi2 = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi2))

        return node

    def parse_function_declaration(self) -> ParseNode:
        # <function-declaration> ::=
        #     KEYWORD(fungsi) IDENTIFIER
        #     [ <formal-parameter-list> ]
        #     COLON <type>
        #     SEMICOLON
        #     <block>
        #     SEMICOLON
        node = ParseNode("<function-declaration>")

        kw = self.expect_keyword("fungsi")
        node.children.append(ParseNode("KEYWORD(fungsi)", token=kw))

        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        if self.current() and self.current().type == TokenType.LPARENTHESIS:
            node.children.append(self.parse_formal_parameter_list())

        colon = self.expect(TokenType.COLON)
        node.children.append(ParseNode("COLON", token=colon))

        node.children.append(self.parse_type())

        semi1 = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi1))

        node.children.append(self.parse_block())

        semi2 = self.expect(TokenType.SEMICOLON)
        node.children.append(ParseNode("SEMICOLON", token=semi2))
        return node

    def parse_formal_parameter_list(self) -> ParseNode:
        node = ParseNode("<formal-parameter-list>")
        lp = self.expect(TokenType.LPARENTHESIS)
        node.children.append(ParseNode("LPARENTHESIS", token=lp))

        node.children.append(self.parse_parameter_group())

        while True:
            if self.current() and self.current().type == TokenType.SEMICOLON:
                semi = self.expect(TokenType.SEMICOLON)
                node.children.append(ParseNode("SEMICOLON", token=semi))
                node.children.append(self.parse_parameter_group())
            else:
                break

        rp = self.expect(TokenType.RPARENTHESIS)
        node.children.append(ParseNode("RPARENTHESIS", token=rp))
        return node

    def parse_parameter_group(self) -> ParseNode:
        node = ParseNode("<parameter-group>")
        node.children.append(self.parse_identifier_list())

        colon = self.expect(TokenType.COLON)
        node.children.append(ParseNode("COLON", token=colon))

        node.children.append(self.parse_type())
        return node

    def parse_block(self) -> ParseNode:
        node = ParseNode("<block>")
        node.children.append(self.parse_declaration_part())
        node.children.append(self.parse_compound_statement())
        return node

    # ========== 4. Compound Statement & Statements ==========
    def parse_compound_statement(self) -> ParseNode:
        node = ParseNode("<compound-statement>")
        mulai = self.expect_keyword("mulai")
        node.children.append(ParseNode("KEYWORD(mulai)", token=mulai))

        node.children.append(self.parse_statement_list())

        selesai = self.expect_keyword("selesai")
        node.children.append(ParseNode("KEYWORD(selesai)", token=selesai))
        return node

    def parse_statement_list(self) -> ParseNode:
        node = ParseNode("<statement-list>")
        
        # Jika langsung menemukan 'selesai' atau 'sampai', return node kosong
        if self.current() and (self.check_keyword("selesai") or self.check_keyword("sampai")):
            return node

        node.children.append(self.parse_statement())

        while True:
            tok = self.current()
            if tok is None or self.check_keyword("selesai") or self.check_keyword("sampai"):
                break
            if tok.type == TokenType.SEMICOLON:
                semi = self.advance()
                node.children.append(ParseNode("SEMICOLON", token=semi))
                # Setelah semicolon, jika berikutnya 'selesai' atau 'sampai', break
                if self.current() and (self.check_keyword("selesai") or self.check_keyword("sampai")):
                    break
                # Jika ada statement setelah semicolon, parse
                if self.current() and not (self.check_keyword("selesai") or self.check_keyword("sampai")):
                    node.children.append(self.parse_statement())
            else:
                # Handle kasus tanpa semicolon (seperti dalam repeat-until)
                # Coba parse statement berikutnya jika bukan keyword khusus
                if not (self.check_keyword("selesai") or self.check_keyword("sampai")):
                    node.children.append(self.parse_statement())
                else:
                    break

        return node

    def parse_statement(self) -> ParseNode:
        node = ParseNode("<statement>")
        tok = self.current()

        if tok is None:
            raise ParserError("Unexpected end of input in <statement>")

        # Handle repeat statement terlebih dahulu
        if self.check_keyword("ulangi"):
            node.children.append(self.parse_repeat_statement())
            return node

        # Compound statement
        if self.check_keyword("mulai"):
            node.children.append(self.parse_compound_statement())
            return node

        # IF
        if self.check_keyword("jika"):
            node.children.append(self.parse_if_statement())
            return node

        # WHILE
        if self.check_keyword("selama"):
            node.children.append(self.parse_while_statement())
            return node

        # FOR
        if self.check_keyword("untuk"):
            node.children.append(self.parse_for_statement())
            return node

        # CASE
        if self.check_keyword("kasus"):
            node.children.append(self.parse_case_statement())
            return node

        # Procedure/function call untuk built-in functions
        if tok.type == TokenType.KEYWORD and tok.value.lower() in ("writeln", "readln", "write", "read"):
            node.children.append(self.parse_procedure_or_function_call())
            return node

        # IDENTIFIER: bisa assignment atau procedure/function-call atau variable access
        if tok.type == TokenType.IDENTIFIER:
            # Look ahead lebih jauh untuk menentukan jenis statement
            # Kita perlu mencari assignment operator (:=) setelah kemungkinan field/array access
            
            # Simpan posisi saat ini untuk backtracking
            saved_pos = self.pos
            
            try:
                # Coba parse sebagai variable (bisa jadi field/array access)
                variable_node = self.parse_variable()
                
                # Sekarang cek apakah berikutnya adalah assignment operator
                if self.current() and self.current().type == TokenType.ASSIGN_OPERATOR:
                    # Ini assignment statement
                    # Kembalikan posisi dan parse ulang dengan parse_assignment_statement
                    self.pos = saved_pos
                    node.children.append(self.parse_assignment_statement())
                else:
                    # Bukan assignment, mungkin procedure call tanpa parameter
                    # Kembalikan posisi dan coba parse sebagai procedure call
                    self.pos = saved_pos
                    
                    # Cek apakah ini function call (ada parentheses)
                    la = self.lookahead()
                    if la and la.type == TokenType.LPARENTHESIS:
                        node.children.append(self.parse_procedure_or_function_call())
                    else:
                        # Anggap sebagai procedure call tanpa parameter
                        ident = self.expect(TokenType.IDENTIFIER)
                        node.children.append(ParseNode("IDENTIFIER", token=ident))
                        
            except ParserError:
                # Jika parse_variable gagal, coba approach lama
                self.pos = saved_pos
                la = self.lookahead()
                
                # Assignment statement (identifier diikuti :=)
                if la and la.type == TokenType.ASSIGN_OPERATOR:
                    node.children.append(self.parse_assignment_statement())
                # Function call (identifier diikuti ( )
                elif la and la.type == TokenType.LPARENTHESIS:
                    node.children.append(self.parse_procedure_or_function_call())
                else:
                    # Procedure call tanpa parameter
                    ident = self.expect(TokenType.IDENTIFIER)
                    node.children.append(ParseNode("IDENTIFIER", token=ident))
                    
            return node

        # Handle empty statement
        if tok.type == TokenType.SEMICOLON:
            self.advance()  # consume the semicolon
            return node  # empty statement

        raise ParserError(
            f"Unexpected token {tok.type.name}('{tok.value}') "
            f"at line {tok.line} in <statement>"
        )

    # ========== 5. Bentuk-bentuk Statement ==========

    # -------- 5.1 Assignment --------
    def parse_assignment_statement(self) -> ParseNode:
        # <assignment-statement> ::= IDENTIFIER ASSIGN_OPERATOR <expression>
        node = ParseNode("<assignment-statement>")
        
        # Gunakan parse_variable bukan hanya identifier
        node.children.append(self.parse_variable())
        
        assign = self.expect(TokenType.ASSIGN_OPERATOR)
        node.children.append(ParseNode("ASSIGN_OPERATOR(:=)", token=assign))

        node.children.append(self.parse_expression())
        return node

    def parse_variable(self) -> ParseNode:
        # Parse variable: bisa identifier sederhana, field access, atau array access
        node = ParseNode("<variable>")
        
        # Mulai dengan identifier
        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))
        
        # Handle field access (p.x) dan array access (m[1,1])
        while True:
            tok = self.current()
            if not tok:
                break
                
            # Field access: identifier.dot.identifier
            if tok.type == TokenType.DOT:
                dot = self.expect(TokenType.DOT)
                node.children.append(ParseNode("DOT", token=dot))
                
                field_ident = self.expect(TokenType.IDENTIFIER)
                node.children.append(ParseNode("IDENTIFIER", token=field_ident))
                
            # Array access: identifier[bracket expression]
            elif tok.type == TokenType.LBRACKET:
                lbr = self.expect(TokenType.LBRACKET)
                node.children.append(ParseNode("LBRACKET", token=lbr))
                
                # Parse index expressions
                node.children.append(self.parse_expression())
                
                # Handle multiple dimensions (comma-separated)
                while self.current() and self.current().type == TokenType.COMMA:
                    comma = self.expect(TokenType.COMMA)
                    node.children.append(ParseNode("COMMA", token=comma))
                    node.children.append(self.parse_expression())
                    
                rbr = self.expect(TokenType.RBRACKET)
                node.children.append(ParseNode("RBRACKET", token=rbr))
                
            else:
                break
                
        return node

    # -------- 5.2 if Statement --------
    def parse_if_statement(self) -> ParseNode:
        # <if-statement> ::=
        #     KEYWORD(jika) <expression> KEYWORD(maka) <statement>
        #     [ KEYWORD(selain-itu) <statement> ]
        node = ParseNode("<if-statement>")
        kj = self.expect_keyword("jika")
        node.children.append(ParseNode("KEYWORD(jika)", token=kj))

        node.children.append(self.parse_expression())

        km = self.expect_keyword("maka")
        node.children.append(ParseNode("KEYWORD(maka)", token=km))

        node.children.append(self.parse_statement())

        if self.check_keyword("selainitu"):
            ke = self.expect_keyword("selainitu")
            node.children.append(ParseNode("KEYWORD(selainitu)", token=ke))
            node.children.append(self.parse_statement())

        return node

    def parse_while_statement(self) -> ParseNode:
        # <while-statement> ::= KEYWORD(selama) <expression> KEYWORD(lakukan) <statement>
        node = ParseNode("<while-statement>")
        ks = self.expect_keyword("selama")
        node.children.append(ParseNode("KEYWORD(selama)", token=ks))

        node.children.append(self.parse_expression())

        kl = self.expect_keyword("lakukan")
        node.children.append(ParseNode("KEYWORD(lakukan)", token=kl))

        node.children.append(self.parse_statement())
        return node

    def parse_for_statement(self) -> ParseNode:
        # <for-statement> ::=
        #     KEYWORD(untuk) IDENTIFIER ASSIGN_OPERATOR <expression>
        #     ( KEYWORD(ke) | KEYWORD(turun-ke) )
        #     <expression>
        #     KEYWORD(lakukan) <statement>
        node = ParseNode("<for-statement>")
        ku = self.expect_keyword("untuk")
        node.children.append(ParseNode("KEYWORD(untuk)", token=ku))

        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        assign = self.expect(TokenType.ASSIGN_OPERATOR)
        node.children.append(ParseNode("ASSIGN_OPERATOR(:=)", token=assign))

        node.children.append(self.parse_expression())

        # ke / turunke
        if self.check_keyword("ke"):
            kdir = self.expect_keyword("ke")
            node.children.append(ParseNode("KEYWORD(ke)", token=kdir))
        elif self.check_keyword("turunke"):
            kdir = self.expect_keyword("turunke")
            node.children.append(ParseNode("KEYWORD(turunke)", token=kdir))
        else:
            raise ParserError("Expected 'ke' or 'turunke' in <for-statement>")

        node.children.append(self.parse_expression())

        kl = self.expect_keyword("lakukan")
        node.children.append(ParseNode("KEYWORD(lakukan)", token=kl))

        node.children.append(self.parse_statement())
        return node

    def parse_repeat_statement(self) -> ParseNode:
        node = ParseNode("<repeat-statement>")
        kulangi = self.expect_keyword("ulangi")
        node.children.append(ParseNode("KEYWORD(ulangi)", token=kulangi))

        # Parse statement list (bisa multiple statements)
        node.children.append(self.parse_statement_list())

        # Pastikan keyword 'sampai' dikenali
        if not self.check_keyword("sampai"):
            tok = self.current()
            raise ParserError(f"Expected 'sampai' after repeat statement, found {tok.type.name if tok else 'EOF'}")
        
        ksampai = self.expect_keyword("sampai")
        node.children.append(ParseNode("KEYWORD(sampai)", token=ksampai))

        node.children.append(self.parse_expression())
        return node

    def parse_case_statement(self) -> ParseNode:
        node = ParseNode("<case-statement>")
        kkasus = self.expect_keyword("kasus")
        node.children.append(ParseNode("KEYWORD(kasus)", token=kkasus))

        node.children.append(self.parse_expression())

        kdari = self.expect_keyword("dari")
        node.children.append(ParseNode("KEYWORD(dari)", token=kdari))

        # Parse case elements sampai menemukan 'selesai'
        while True:
            if self.current() is None:
                raise ParserError("Unexpected EOF in case statement")
            if self.check_keyword("selesai"):
                break
            try:
                node.children.append(self.parse_case_element())
                # Setelah case element, mungkin ada semicolon
                if self.current() and self.current().type == TokenType.SEMICOLON:
                    self.advance()  # skip semicolon antara case elements
            except ParserError as e:
                # Jika gagal parse case element, cek apakah ini akhir case statement
                if self.check_keyword("selesai"):
                    break
                else:
                    raise e

        kselesai = self.expect_keyword("selesai")
        node.children.append(ParseNode("KEYWORD(selesai)", token=kselesai))
        return node

    def parse_case_element(self) -> ParseNode:
        node = ParseNode("<case-element>")
        node.children.append(self.parse_constant_list())

        colon = self.expect(TokenType.COLON)
        node.children.append(ParseNode("COLON", token=colon))

        node.children.append(self.parse_statement())
        return node

    def parse_constant_list(self) -> ParseNode:
        node = ParseNode("<constant-list>")
        node.children.append(self.parse_const_value())

        while True:
            if self.current() and self.current().type == TokenType.COMMA:
                comma = self.expect(TokenType.COMMA)
                node.children.append(ParseNode("COMMA", token=comma))
                node.children.append(self.parse_const_value())
            else:
                break
        return node

    # ========== 6. Procedure/Function Call ==========
    def parse_procedure_or_function_call(self) -> ParseNode:
        node = ParseNode("<procedure-call>")
        tok = self.current()

        if tok is None:
            raise ParserError("Unexpected EOF in <procedure-call>")

        # Untuk identifier, cek dulu apakah ini variable access atau function call
        if tok.type == TokenType.IDENTIFIER:
            # Look ahead untuk menentukan apakah ini function call atau variable
            la = self.lookahead()
            if la and la.type == TokenType.LPARENTHESIS:
                # Function call
                ident = self.expect(TokenType.IDENTIFIER)
                node.children.append(ParseNode("IDENTIFIER", token=ident))

                lp = self.expect(TokenType.LPARENTHESIS)
                node.children.append(ParseNode("LPARENTHESIS", token=lp))

                if self.current() and self.current().type != TokenType.RPARENTHESIS:
                    node.children.append(self.parse_parameter_list())

                rp = self.expect(TokenType.RPARENTHESIS)
                node.children.append(ParseNode("RPARENTHESIS", token=rp))
            else:
                # Bukan function call, mungkin variable access
                node.children.append(self.parse_variable())
                
        elif tok.type == TokenType.KEYWORD and tok.value.lower() in ("writeln", "readln", "write", "read"):
            kw = self.expect_keyword(tok.value.lower())
            node.children.append(ParseNode(f"KEYWORD({kw.value.lower()})", token=kw))

            # Parameter list untuk built-in functions
            if self.current() and self.current().type == TokenType.LPARENTHESIS:
                lp = self.expect(TokenType.LPARENTHESIS)
                node.children.append(ParseNode("LPARENTHESIS", token=lp))

                if self.current() and self.current().type != TokenType.RPARENTHESIS:
                    node.children.append(self.parse_parameter_list())

                rp = self.expect(TokenType.RPARENTHESIS)
                node.children.append(ParseNode("RPARENTHESIS", token=rp))

        else:
            raise ParserError("Expected identifier or built-in procedure in <procedure-call>")

        return node

    def parse_parameter_list(self) -> ParseNode:
        # <parameter-list> ::= <expression> { COMMA <expression> }
        node = ParseNode("<parameter-list>")
        node.children.append(self.parse_expression())

        while True:
            if self.current() and self.current().type == TokenType.COMMA:
                comma = self.expect(TokenType.COMMA)
                node.children.append(ParseNode("COMMA", token=comma))
                node.children.append(self.parse_expression())
            else:
                break
        return node

    def parse_function_call(self) -> ParseNode:
        # <function-call> ::= IDENTIFIER LPARENTHESIS [ <parameter-list> ] RPARENTHESIS
        node = ParseNode("<function-call>")
        ident = self.expect(TokenType.IDENTIFIER)
        node.children.append(ParseNode("IDENTIFIER", token=ident))

        lp = self.expect(TokenType.LPARENTHESIS)
        node.children.append(ParseNode("LPARENTHESIS", token=lp))

        if self.current() and self.current().type != TokenType.RPARENTHESIS:
            node.children.append(self.parse_parameter_list())

        rp = self.expect(TokenType.RPARENTHESIS)
        node.children.append(ParseNode("RPARENTHESIS", token=rp))
        return node

    # ========== 7. Ekspresi dan Operator ==========
    def parse_expression(self) -> ParseNode:
        # <expression> ::= <simple-expression> [ <relational-operator> <simple-expression> ]
        node = ParseNode("<expression>")
        node.children.append(self.parse_simple_expression())

        tok = self.current()
        if tok and tok.type == TokenType.RELATIONAL_OPERATOR:
            node.children.append(self.parse_relational_operator())
            node.children.append(self.parse_simple_expression())

        return node

    def parse_relational_operator(self) -> ParseNode:
        # <relational-operator> ::= = | <> | < | <= | > | >=
        node = ParseNode("<relational-operator>")
        tok = self.expect(TokenType.RELATIONAL_OPERATOR)
        node.children.append(ParseNode(f"RELATIONAL_OPERATOR({tok.value})", token=tok))
        return node

    def parse_simple_expression(self) -> ParseNode:
        # <simple-expression> ::= [ <unary-add-operator> ] <term> { <additive-operator> <term> }
        node = ParseNode("<simple-expression>")

        # Check for unary operator
        tok = self.current()
        if tok and tok.type == TokenType.ARITHMETIC_OPERATOR and tok.value in ("+", "-"):
            node.children.append(self.parse_unary_add_operator())

        node.children.append(self.parse_term())

        while True:
            tok = self.current()
            if not tok:
                break
                
            is_add_op = (tok.type == TokenType.ARITHMETIC_OPERATOR and tok.value in ("+", "-"))
            is_or_op = (tok.type == TokenType.LOGICAL_OPERATOR and tok.value.lower() == "atau")
            
            if is_add_op or is_or_op:
                node.children.append(self.parse_additive_operator())
                node.children.append(self.parse_term())
            else:
                break

        return node
    
    def parse_simple_expression_for_range(self) -> ParseNode:
        # Versi khusus untuk parsing dalam range yang hanya menerima numbers/identifiers sederhana
        node = ParseNode("<simple-expression>")
        tok = self.current()
        
        if tok is None:
            raise ParserError("Unexpected EOF in range expression")
        
        # Dalam range, kita hanya expect number atau identifier sederhana
        if tok.type == TokenType.NUMBER:
            num = self.expect(TokenType.NUMBER)
            node.children.append(ParseNode("NUMBER", token=num))
        elif tok.type == TokenType.IDENTIFIER:
            ident = self.expect(TokenType.IDENTIFIER)
            node.children.append(ParseNode("IDENTIFIER", token=ident))
        else:
            raise ParserError(f"Expected NUMBER or IDENTIFIER in range, found {tok.type.name}({tok.value})")
        
        return node

    def parse_term(self) -> ParseNode:
        # <term> ::= <factor> { <multiplicative-operator> <factor> }
        node = ParseNode("<term>")
        node.children.append(self.parse_factor())

        while True:
            tok = self.current()
            if not tok:
                break
                
            is_mult_op = (
                (tok.type == TokenType.ARITHMETIC_OPERATOR and tok.value in ("*", "/", "bagi", "mod"))
            )
            is_and_op = (tok.type == TokenType.LOGICAL_OPERATOR and tok.value.lower() == "dan")
            
            if is_mult_op or is_and_op:
                node.children.append(self.parse_multiplicative_operator())
                node.children.append(self.parse_factor())
            else:
                break

        return node

    def parse_factor(self) -> ParseNode:
        # <factor> ::=
        #     IDENTIFIER
        #   | NUMBER
        #   | CHAR_LITERAL
        #   | STRING_LITERAL
        #   | LPARENTHESIS <expression> RPARENTHESIS
        #   | LOGICAL_OPERATOR(tidak) <factor>
        #   | <function-call>
        node = ParseNode("<factor>")
        tok = self.current()

        if tok is None:
            raise ParserError("Unexpected EOF in <factor>")

        # function-call vs IDENTIFIER vs VARIABLE
        if tok.type == TokenType.IDENTIFIER:
            la = self.lookahead()
            
            # Cek jika ini function call atau variable access
            if la and la.type == TokenType.LPARENTHESIS:
                node.children.append(self.parse_function_call())
            else:
                # Bisa jadi identifier sederhana atau variable dengan field/array access
                # Cek lookahead lebih jauh untuk menentukan
                if (la and (la.type == TokenType.DOT or la.type == TokenType.LBRACKET)):
                    # Ini variable dengan field/array access
                    node.children.append(self.parse_variable())
                else:
                    # Identifier sederhana
                    ident = self.expect(TokenType.IDENTIFIER)
                    node.children.append(ParseNode("IDENTIFIER", token=ident))
            return node

        if tok.type == TokenType.NUMBER:
            num = self.expect(TokenType.NUMBER)
            node.children.append(ParseNode("NUMBER", token=num))
            return node

        if tok.type == TokenType.CHAR_LITERAL:
            ch = self.expect(TokenType.CHAR_LITERAL)
            node.children.append(ParseNode("CHAR_LITERAL", token=ch))
            return node

        if tok.type == TokenType.STRING_LITERAL:
            st = self.expect(TokenType.STRING_LITERAL)
            node.children.append(ParseNode("STRING_LITERAL", token=st))
            return node

        if tok.type == TokenType.LPARENTHESIS:
            lp = self.expect(TokenType.LPARENTHESIS)
            node.children.append(ParseNode("LPARENTHESIS", token=lp))
            node.children.append(self.parse_expression())
            rp = self.expect(TokenType.RPARENTHESIS)
            node.children.append(ParseNode("RPARENTHESIS", token=rp))
            return node

        # LOGICAL_OPERATOR(tidak) + factor
        if tok.type == TokenType.LOGICAL_OPERATOR and tok.value.lower() == "tidak":
            log = self.expect(TokenType.LOGICAL_OPERATOR)
            node.children.append(ParseNode("LOGICAL_OPERATOR(tidak)", token=log))
            node.children.append(self.parse_factor())
            return node

        raise ParserError(
            f"Unexpected token {tok.type.name}('{tok.value}') in <factor>"
        )

    # ========== Operator Helpers ==========
    def parse_unary_add_operator(self) -> ParseNode:
        # <unary-add-operator> ::= + | -
        node = ParseNode("<unary-add-operator>")
        tok = self.current()
        if not (tok and tok.type == TokenType.ARITHMETIC_OPERATOR and tok.value in ("+", "-")):
            raise ParserError("Expected '+' or '-' in <unary-add-operator>")
        op = self.expect(TokenType.ARITHMETIC_OPERATOR)
        node.children.append(ParseNode(f"ARITHMETIC_OPERATOR({op.value})", token=op))
        return node

    def parse_additive_operator(self) -> ParseNode:
        # <additive-operator> ::= + | - | atau
        node = ParseNode("<additive-operator>")
        tok = self.current()

        if tok is None:
            raise ParserError("Unexpected EOF in <additive-operator>")

        if tok.type == TokenType.ARITHMETIC_OPERATOR and tok.value in ("+", "-"):
            op = self.expect(TokenType.ARITHMETIC_OPERATOR)
            node.children.append(ParseNode(f"ARITHMETIC_OPERATOR({op.value})", token=op))
            return node

        if tok.type == TokenType.LOGICAL_OPERATOR and tok.value.lower() == "atau":
            op = self.expect(TokenType.LOGICAL_OPERATOR)
            node.children.append(ParseNode("LOGICAL_OPERATOR(atau)", token=op))
            return node

        raise ParserError("Expected '+', '-' or 'atau' in <additive-operator>")

    def parse_multiplicative_operator(self) -> ParseNode:
        # <multiplicative-operator> ::= *, /, bagi, mod, dan
        node = ParseNode("<multiplicative-operator>")
        tok = self.current()

        if tok is None:
            raise ParserError("Unexpected EOF in <multiplicative-operator>")

        # *, /, bagi, mod -> ARITHMETIC_OPERATOR
        if tok.type == TokenType.ARITHMETIC_OPERATOR and tok.value in ("*", "/", "bagi", "mod"):
            op = self.expect(TokenType.ARITHMETIC_OPERATOR)
            node.children.append(ParseNode(f"ARITHMETIC_OPERATOR({op.value})", token=op))
            return node

        # dan -> LOGICAL_OPERATOR
        if tok.type == TokenType.LOGICAL_OPERATOR and tok.value.lower() == "dan":
            op = self.expect(TokenType.LOGICAL_OPERATOR)
            node.children.append(ParseNode("LOGICAL_OPERATOR(dan)", token=op))
            return node

        raise ParserError("Expected multiplicative operator in <multiplicative-operator>")