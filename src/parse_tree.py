from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from src.tokens import Token

@dataclass
class ParseNode:
    name: str
    children: List["ParseNode"] = field(default_factory=list)
    token: Optional[Token] = None

    def add_child(self, child: "ParseNode") -> None:
        self.children.append(child)


def print_tree(root: ParseNode) -> None:
    print(root.name)
    print_tree_recursive(root.children, "")


def print_tree_recursive(nodes: List[ParseNode], prefix: str) -> None:
    for i, node in enumerate(nodes):
        is_last = (i == len(nodes) - 1)
        connector = "└── " if is_last else "├── "
        
        if node.token is not None:
            label = f"{node.token.type.name}({node.token.value})"
        else:
            label = node.name
        
        print(prefix + connector + label)
        
        processed_children = process_children(node)
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree_recursive(processed_children, new_prefix)


def process_children(node: ParseNode) -> List[ParseNode]:
    processed = []
    
    for child in node.children:
        if child.name == "<statement>" and child.token is None:
            processed.extend(process_children(child))
        elif child.name == "<var-declaration>" and node.name == "<var-declaration>":
            processed.extend(process_children(child))
        elif child.name == "<procedure/function-call>":
            new_child = ParseNode("<procedure-call>", child.children, child.token)
            processed.append(new_child)
        elif child.name in ["<additive-operator>", "<multiplicative-operator>", "<relational-operator>"]:
            if child.children and child.children[0].token:
                operator_token = child.children[0].token
                processed.append(ParseNode(
                    f"{operator_token.type.name}({operator_token.value})",
                    [],
                    operator_token
                ))
            else:
                processed.append(child)
        else:
            processed.append(child)
    
    return processed