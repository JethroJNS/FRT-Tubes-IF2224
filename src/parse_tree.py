# src/parse_tree.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from src.tokens import Token

@dataclass
class ParseNode:
    # name      : nama non-terminal atau token, misalnya : "<program>", "IDENTIFIER"
    # token     : Token asli (kalau leaf / terminal)
    # children  : daftar anak (untuk non-terminal)

    name: str
    children: List["ParseNode"] = field(default_factory=list)
    token: Optional[Token] = None

    def add_child(self, child: "ParseNode") -> None:
        self.children.append(child)


def print_parse_tree(node: ParseNode, prefix: str = "", is_last: bool = True) -> None:
    # mencetak parse tree
    connector = "└── " if is_last else "├── "

    if node.token is not None: # leaf 
        label = f"{node.name}({node.token.value})" # menampilkan TOKEN_TYPE(lexeme)
    else: # non-terminal
        label = node.name # hanya menampilkan nama non-terminal

    print(prefix + connector + label)

    # prefix untuk anak
    child_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_parse_tree(child, child_prefix, is_last_child)
