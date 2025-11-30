from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass, field
from src.tokens import Token
from .symbol_table import BaseType

@dataclass
class ASTNode:
    node_type: str
    children: List[ASTNode] = field(default_factory=list)
    token: Optional[Token] = None
    data_type: Optional[BaseType] = None
    tab_index: int = -1
    block_index: int = -1
    
    def add_child(self, child: ASTNode):
        self.children.append(child)
        
    def __repr__(self):
        return f"{self.node_type}(type={self.data_type}, tab_idx={self.tab_index})"

@dataclass
class ProgramNode(ASTNode):
    name: str = ""
    
    def __repr__(self):
        return f"ProgramNode(name: '{self.name}')"

@dataclass
class VarDeclNode(ASTNode):
    identifier: str = ""
    
    def __repr__(self):
        return f"VarDecl('{self.identifier}')"

@dataclass
class AssignmentNode(ASTNode):
    def __repr__(self):
        if len(self.children) >= 2:
            target = self.children[0]
            value = self.children[1]
            
            if isinstance(target, VariableNode):
                target_str = f"'{target.identifier}'"
            else:
                target_str = str(target)
                
            if isinstance(value, BinaryExpressionNode):
                # Ambil left dan right dari BinaryExpressionNode
                if len(value.children) >= 2:
                    left = value.children[0]
                    right = value.children[1]
                    left_str = f"'{left.identifier}'" if isinstance(left, VariableNode) else str(left)
                    right_str = str(right)
                    value_str = f"{left_str}{value.operator}{right_str}"
                else:
                    value_str = str(value)
            else:
                value_str = str(value)
                
            return f"Assign({target_str} := {value_str})"
        elif len(self.children) == 1:
            return f"Assign({self.children[0]} := ?)"
        else:
            return "Assign(?)"

@dataclass
class BinaryExpressionNode(ASTNode):
    operator: str = ""
    
    def __repr__(self):
        if len(self.children) >= 2:
            left = self.children[0]
            right = self.children[1]
            left_str = f"'{left.identifier}'" if isinstance(left, VariableNode) else str(left)
            right_str = str(right)
            return f"{left_str}{self.operator}{right_str}"
        return f"BinOp '{self.operator}'"

@dataclass
class VariableNode(ASTNode):
    identifier: str = ""
    
    def __repr__(self):
        return f"Var('{self.identifier}')"

@dataclass
class NumberNode(ASTNode):
    value: int = 0
    
    def __repr__(self):
        return f"{self.value}"

@dataclass
class StringNode(ASTNode):
    value: str = ""
    
    def __repr__(self):
        return f"String('{self.value}')"
    
@dataclass
class BooleanNode(ASTNode):
    value: bool = False
    identifier: str = ""
    
    def __repr__(self):
        return f"Boolean('{self.identifier}')"

@dataclass  
class ArrayElementNode(VariableNode):
    is_array_element: bool = True
    
    def __repr__(self):
        return f"ArrayElement('{self.identifier}')"

@dataclass
class ProcedureCallNode(ASTNode):
    procedure_name: str = ""
    
    def __repr__(self):
        args = ", ".join(str(child) for child in self.children) if self.children else ""
        return f"ProcedureCall(name: '{self.procedure_name}', args: [{args}])"