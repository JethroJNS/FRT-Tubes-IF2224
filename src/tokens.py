from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    KEYWORD = auto()
    LOGICAL_OPERATOR = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    CHAR_LITERAL = auto()
    STRING_LITERAL = auto()
    ARITHMETIC_OPERATOR = auto()
    RELATIONAL_OPERATOR = auto()
    ASSIGN_OPERATOR = auto()
    SEMICOLON = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    LPARENTHESIS = auto()
    RPARENTHESIS = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    RANGE_OPERATOR = auto()
    WHITESPACE = auto()
    UNKNOWN = auto()

KEYWORDS = {
    "program","var","begin","end","if","then","else","while","do","for","to","downto",
    "integer","real","boolean","char","array","of","procedure","function","const","type"
}

WORD_LOGICAL = {"and","or","not"}
WORD_ARITH = {"div","mod"}

ARITH_SYMBOL = {"+","-","*","/"}
REL_OPS = {"=","<>","<","<=",">",">="}
ASSIGN = {":="}
RANGE = {".."}

PUNCTUATION = {
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ".": TokenType.DOT,
    "(": TokenType.LPARENTHESIS,
    ")": TokenType.RPARENTHESIS,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
}

LONGEST_FIRST = ["(*", "*)", ":=", "..", "<=", ">=", "<>"]

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

def classify_word_or_operator_word(lexeme: str) -> TokenType:
    low = lexeme.lower()
    if low in KEYWORDS:
        return TokenType.KEYWORD
    if low in WORD_LOGICAL:
        return TokenType.LOGICAL_OPERATOR
    if low in WORD_ARITH:
        return TokenType.ARITHMETIC_OPERATOR
    return TokenType.IDENTIFIER

def classify_punct_or_ops(lexeme: str) -> TokenType | None:
    if lexeme in ASSIGN:
        return TokenType.ASSIGN_OPERATOR
    if lexeme in RANGE:
        return TokenType.RANGE_OPERATOR
    if lexeme in REL_OPS:
        return TokenType.RELATIONAL_OPERATOR
    if lexeme in ARITH_SYMBOL:
        return TokenType.ARITHMETIC_OPERATOR
    if lexeme in PUNCTUATION:
        return PUNCTUATION[lexeme]
    return None