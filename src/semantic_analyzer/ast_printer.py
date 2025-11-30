from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass, field
from src.parse_tree import ParseNode
from src.tokens import Token, TokenType
from .symbol_table import SymbolTable, ObjType, BaseType
from .ast_nodes import *
from .semantic_analyzer import SemanticAnalyzer 

def print_decorated_ast(node: ASTNode, level: int = 0, prefix: str = "", is_last: bool = True):
    
    if level == 0:
        connector = ""
        child_prefix = ""
    else:
        connector = " └─ " if is_last else " ├─ "
        child_prefix = "    " if is_last else " │  "
    
    if isinstance(node, ProgramNode):
        print(f"ProgramNode(name: '{node.name}')")
        
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            new_prefix = prefix + child_prefix
            print_decorated_ast(child, level + 1, new_prefix, is_last_child)
            
    elif node.node_type == "Declarations":
        print(prefix + connector + "Declarations")
        
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            new_prefix = prefix + child_prefix
            print_decorated_ast(child, level + 1, new_prefix, is_last_child)
                
    elif isinstance(node, VarDeclNode):
        decorators = []
        if node.tab_index >= 0:
            decorators.append(f"tab_index:{node.tab_index}")
        if node.data_type:
            decorators.append(f"type:{node.data_type.name.lower()}")
        decorators.append(f"lev:{node.block_index}") # Gunakan block_index sebagai level
        
        decorator_str = f" → {', '.join(decorators)}"
        print(prefix + connector + f"VarDecl('{node.identifier}'){decorator_str}")

    elif node.node_type == "ProcedureDeclaration":
        decorators = []
        if node.tab_index >= 0:
            decorators.append(f"tab_index:{node.tab_index}")
        if hasattr(node, 'procedure_name'):
            decorators.append(f"name:{node.procedure_name}")
        
        decorator_str = f" → {', '.join(decorators)}" if decorators else ""
        print(prefix + connector + f"ProcedureDecl{decorator_str}")

    elif node.node_type == "FunctionDeclaration":
        decorators = []
        if node.tab_index >= 0:
            decorators.append(f"tab_index:{node.tab_index}")
        if node.data_type:
            decorators.append(f"return_type:{node.data_type.name.lower()}")
        if hasattr(node, 'function_name'):
            decorators.append(f"name:{node.function_name}")
        
        decorator_str = f" → {', '.join(decorators)}" if decorators else ""
        print(prefix + connector + f"FunctionDecl{decorator_str}")
        
    elif node.node_type == "ConstItem":
        # Print Constant declaration
        decorators = []
        if node.tab_index >= 0:
            decorators.append(f"tab_index:{node.tab_index}")
        if node.data_type:
            decorators.append(f"type:{node.data_type.name.lower()}")
        decorators.append(f"lev:0")
        
        decorator_str = f" → {', '.join(decorators)}"
        print(prefix + connector + f"ConstDecl{decorator_str}")
        
    elif node.node_type == "TypeItem":
        # Print Type declaration
        decorators = []
        if node.tab_index >= 0:
            decorators.append(f"tab_index:{node.tab_index}")
        if node.data_type:
            decorators.append(f"type:{node.data_type.name.lower()}")
        decorators.append(f"lev:0")
        
        decorator_str = f" → {', '.join(decorators)}"
        print(prefix + connector + f"TypeDecl{decorator_str}")
        
    elif node.node_type == "CompoundStatement":
        # Print Block
        decorators = []
        if node.block_index >= 0:
            decorators.append(f"block_index:{node.block_index}")
        decorators.append(f"lev:1")
        
        decorator_str = f" → {', '.join(decorators)}" if decorators else ""
        print(prefix + connector + f"Block{decorator_str}")
        
        # Process statements
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            new_prefix = prefix + child_prefix
            print_decorated_ast(child, level + 1, new_prefix, is_last_child)
            
    elif isinstance(node, AssignmentNode):
        # Print Assignment statement
        if len(node.children) >= 2:
            target = node.children[0]
            value = node.children[1]
            
            # Format target
            if isinstance(target, VariableNode):
                target_str = f"'{target.identifier}'"
            else:
                target_str = str(target)
                
            if isinstance(value, BinaryExpressionNode):
                if len(value.children) >= 2:
                    left = value.children[0]
                    right = value.children[1]
                    left_str = f"'{left.identifier}'" if isinstance(left, VariableNode) else str(left)
                    right_str = str(right)
                    value_str = f"{left_str}{value.operator}{right_str}"
                else:
                    value_str = str(value)
            elif isinstance(value, (NumberNode, VariableNode)):
                value_str = str(value)
            else:
                value_str = str(value)
                
            assign_str = f"Assign({target_str} := {value_str})"
        else:
            assign_str = "Assign(?)"
            
        decorators = []
        if node.data_type:
            decorators.append(f"type:{node.data_type.name.lower()}")
            
        decorator_str = f" → {', '.join(decorators)}" if decorators else ""
        print(prefix + connector + f"{assign_str}{decorator_str}")
        
        # Print children details
        if len(node.children) >= 2:
            target = node.children[0]
            value = node.children[1]
            
            if isinstance(target, VariableNode):
                decorators = []
                if target.tab_index >= 0:
                    decorators.append(f"tab_index:{target.tab_index}")
                if target.data_type:
                    decorators.append(f"type:{target.data_type.name.lower()}")
                    
                decorator_str = f" → {', '.join(decorators)}" if decorators else ""
                print(prefix + child_prefix + " ├─ " + f"target '{target.identifier}'{decorator_str}")
            
            if isinstance(value, BinaryExpressionNode):
                decorators = []
                if value.data_type:
                    decorators.append(f"type:{value.data_type.name.lower()}")
                    
                decorator_str = f" → {', '.join(decorators)}" if decorators else ""
                print(prefix + child_prefix + " └─ " + f"BinOp '{value.operator}'{decorator_str}")
                
                # Print BinOp children
                if len(value.children) >= 2:
                    left = value.children[0]
                    right = value.children[1]
                    
                    # Left operand
                    if isinstance(left, (VariableNode, NumberNode)):
                        left_decorators = []
                        if hasattr(left, 'tab_index') and left.tab_index >= 0:
                            left_decorators.append(f"tab_index:{left.tab_index}")
                        if left.data_type:
                            left_decorators.append(f"type:{left.data_type.name.lower()}")
                            
                        left_decorator_str = f" → {', '.join(left_decorators)}" if left_decorators else ""
                        left_repr = f"'{left.identifier}'" if isinstance(left, VariableNode) else str(left)
                        print(prefix + child_prefix + "     ├─ " + f"{left_repr}{left_decorator_str}")
                    
                    # Right operand
                    if isinstance(right, (VariableNode, NumberNode)):
                        right_decorators = []
                        if hasattr(right, 'tab_index') and right.tab_index >= 0:
                            right_decorators.append(f"tab_index:{right.tab_index}")
                        if right.data_type:
                            right_decorators.append(f"type:{right.data_type.name.lower()}")
                            
                        right_decorator_str = f" → {', '.join(right_decorators)}" if right_decorators else ""
                        right_repr = f"'{right.identifier}'" if isinstance(right, VariableNode) else str(right)
                        print(prefix + child_prefix + "     └─ " + f"{right_repr}{right_decorator_str}")
            else:
                decorators = []
                if value.data_type:
                    decorators.append(f"type:{value.data_type.name.lower()}")
                    
                decorator_str = f" → {', '.join(decorators)}" if decorators else ""
                value_repr = f"'{value.identifier}'" if isinstance(value, VariableNode) else str(value)
                print(prefix + child_prefix + " └─ " + f"value {value_repr}{decorator_str}")

    elif isinstance(node, ProcedureCallNode):
        # Print procedure call
        decorators = []
        if node.tab_index >= 0:
            if node.procedure_name in ['writeln', 'readln', 'write', 'read']:
                decorators.append("predefined")
            decorators.append(f"tab_index:{node.tab_index}")
            
        decorator_str = f" → {', '.join(decorators)}" if decorators else ""
        print(prefix + connector + f"{node.procedure_name}(...){decorator_str}")
        
    else:
        # Skip nodes yang tidak perlu ditampilkan secara eksplisit
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            new_prefix = prefix + child_prefix
            print_decorated_ast(child, level + 1, new_prefix, is_last_child)

def print_symbol_tables(analyzer: SemanticAnalyzer):
    print("\n=== SYMBOL TABLES ===")
    
    print("\nIdentifier Table (tab):")
    print("Idx  Name        Obj        Type    Ref  Nrm  Lev  Adr  Link")
    print("-" * 60)
    for i, entry in enumerate(analyzer.symbol_table.tab):
        if entry is not None:
            obj_name = entry['obj'].name if isinstance(entry['obj'], ObjType) else str(entry['obj'])
            type_name = BaseType(entry['type']).name if entry['type'] in [t.value for t in BaseType] else str(entry['type'])
            print(f"{i:3}  {entry['name']:10}  {obj_name:10}  {type_name:6}  {entry['ref']:3}  {entry['nrm']:3}  {entry['lev']:3}  {entry['adr']:3}  {entry['link']:4}")
        elif i >= analyzer.symbol_table.user_id_start:
            # Tampilkan empty slot untuk user identifiers
            print(f"{i:3}  {'-':10}  {'-':10}  {'-':6}  {'-':3}  {'-':3}  {'-':3}  {'-':3}  {'-':4}")
    
    print("\nBlock Table (btab):")
    print("Idx  Last  Lpar  Psze  Vsze")
    print("-" * 25)
    for i, entry in enumerate(analyzer.symbol_table.btab):
        print(f"{i:3}  {entry['last']:4}  {entry['lpar']:4}  {entry['psze']:4}  {entry['vsze']:4}")
    
    print("\nArray Table (atab):")
    if analyzer.symbol_table.atab:
        print("Idx  IdxType  ElemType  Eref  Low  High  ElemSize  Size")
        print("-" * 50)
        for i, entry in enumerate(analyzer.symbol_table.atab):
            idx_type = BaseType(entry['index_type']).name if entry['index_type'] in [t.value for t in BaseType] else str(entry['index_type'])
            elem_type = BaseType(entry['element_type']).name if entry['element_type'] in [t.value for t in BaseType] else str(entry['element_type'])
            print(f"{i:3}  {idx_type:7}  {elem_type:8}  {entry['eref']:4}  {entry['low']:3}  {entry['high']:4}  {entry['element_size']:8}  {entry['size']:4}")
    else:
        print("(empty)")