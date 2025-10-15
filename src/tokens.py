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
    COMMENT_START = auto()
    COMMENT_END = auto()
    WHITESPACE = auto()
    UNKNOWN = auto()

KEYWORDS = {
    "program","var","begin","end","if","then","else","while","do","for","to","downto",
    "integer","real","boolean","char","array","of","procedure","function","const","type"
}

LOGICAL_OPS = {"and","or","not"}  

ARITH_OPS_SYMBOL = {"+","-","*","/"}
ARITH_OPS_WORD = {"div","mod"}

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

COMMENTS = {
    "brace": {"start": "{", "end": "}"},
    "paren_star": {"start": "(*", "end": "*)"},
}

LONGEST_FIRST = ["(*", "*)", ":=", "..", "<=", ">=", "<>"]

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

def classify_word(lexeme: str) -> TokenType:
    low = lexeme.lower()
    if low in KEYWORDS: return TokenType.KEYWORD
    if low in LOGICAL_OPS: return TokenType.LOGICAL_OPERATOR
    if low in ARITH_OPS_WORD: return TokenType.ARITHMETIC_OPERATOR
    if low in REL_OPS: return TokenType.RELATIONAL_OPERATOR
    return TokenType.IDENTIFIER