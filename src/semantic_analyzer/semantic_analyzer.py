from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass, field
from src.parse_tree import ParseNode
from src.tokens import Token, TokenType
from .symbol_table import SymbolTable, ObjType, BaseType
from .ast_nodes import *

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_ast: Optional[ASTNode] = None
        self.errors: List[str] = []
        
    def analyze(self, parse_tree: ParseNode) -> ASTNode:
        self.errors.clear()
        
        # Start dengan global scope - block 0
        global_block_idx = self.symbol_table.enter_block()
        
        # Build AST and perform semantic analysis
        self.current_ast = self.visit(parse_tree)
        
        # Validasi semua variabel telah diinisialisasi
        self.validate_variable_initialization()
        
        # Leave global scope
        self.symbol_table.leave_block()
        
        return self.current_ast

    def error(self, message: str, token: Token = None):
        if token:
            location = f" at line {token.line}, column {token.column}"
        else:
            location = ""
        self.errors.append(f"Semantic Error{location}: {message}")
    
    def get_type_name(self, type_enum: BaseType) -> str:
        return type_enum.name.lower()
    
    def find_base_type(self, type_node: ParseNode) -> BaseType:
        if type_node.children:
            first_child = type_node.children[0]
            if first_child.token:
                token_value = first_child.token.value.lower()
                if token_value == "integer":
                    return BaseType.INTEGER
                elif token_value == "real":
                    return BaseType.REAL
                elif token_value == "boolean":
                    return BaseType.BOOLEAN
                elif token_value == "char":
                    return BaseType.CHAR
                elif token_value == "string":
                    return BaseType.STRING
        return BaseType.VOID
    
    def extract_identifiers(self, node: ParseNode) -> List[str]:
        identifiers = []
        for child in node.children:
            if child.name == "IDENTIFIER" and child.token:
                identifiers.append(child.token.value)
        return identifiers
    
    def evaluate_constant_expression(self, expr_node: ParseNode) -> Optional[int]:
        if expr_node.name == "<simple-expression>":
            if expr_node.children and expr_node.children[0].name == "<term>":
                term_node = expr_node.children[0]
                if term_node.children and term_node.children[0].name == "<factor>":
                    factor_node = term_node.children[0]
                    if factor_node.children:
                        first_child = factor_node.children[0]
                        if first_child.name == "NUMBER" and first_child.token:
                            try:
                                return int(first_child.token.value)
                            except ValueError:
                                return None
                        elif first_child.name == "IDENTIFIER" and first_child.token:
                            # Look up constant value in symbol table
                            const_name = first_child.token.value
                            const_value = self.symbol_table.get_constant_value(const_name)
                            if const_value is not None:
                                return const_value
                            else:
                                # Mencari constant di symbol table
                                const_idx = self.symbol_table.find_identifier(const_name)
                                if const_idx is not None and self.symbol_table.tab[const_idx]["obj"] == ObjType.CONSTANT:
                                    stored_value = self.symbol_table.get_constant_value(const_name)
                                    if stored_value is not None:
                                        return stored_value
        return None
    
    def parse_range(self, index_spec_node: ParseNode) -> tuple[int, int]:
        low_bound = 1
        high_bound = 10
        
        for child in index_spec_node.children:
            if child.name == "<range>":
                range_children = child.children
                if len(range_children) >= 3:
                    # Parse lower bound
                    low_expr = range_children[0]
                    low_value = self.evaluate_constant_expression(low_expr)
                    if low_value is not None:
                        low_bound = low_value
                    
                    # Parse upper bound  
                    high_expr = range_children[2]
                    high_value = self.evaluate_constant_expression(high_expr)
                    if high_value is not None:
                        high_bound = high_value
        
        return low_bound, high_bound

    def is_type_compatible(self, target_type: BaseType, source_type: BaseType, is_parameter: bool = False) -> bool:
        if target_type == source_type:
            return True
        
        if target_type == BaseType.REAL and source_type == BaseType.INTEGER:
            return True
            
        if is_parameter:
            if target_type == BaseType.INTEGER and source_type == BaseType.REAL:
                return False  # Real tidak bisa ke integer parameter
            if target_type == BaseType.BOOLEAN and source_type != BaseType.BOOLEAN:
                return False  # Hanya boolean ke boolean
            if target_type == BaseType.CHAR and source_type != BaseType.CHAR:
                return False  # Hanya char ke char
                
        # Char dapat diassign ke string
        if target_type == BaseType.STRING and source_type == BaseType.CHAR:
            return True
            
        # Boolean literals compatibility
        if target_type == BaseType.BOOLEAN and source_type == BaseType.BOOLEAN:
            return True
            
        # VOID type
        if target_type == BaseType.VOID or source_type == BaseType.VOID:
            return True
                
        return False
    
    def get_expression_type(self, left_type: BaseType, right_type: BaseType, operator: str) -> BaseType:
        # Handle None types
        if left_type is None:
            left_type = BaseType.VOID
        if right_type is None:
            right_type = BaseType.VOID
            
        # Arithmetic operators
        if operator in ['+', '-', '*', '/', 'bagi', 'mod']:
            if left_type == BaseType.REAL or right_type == BaseType.REAL:
                return BaseType.REAL
            elif left_type == BaseType.INTEGER and right_type == BaseType.INTEGER:
                return BaseType.INTEGER
            else:
                return BaseType.VOID
        
        # Relational operators
        elif operator in ['=', '<>', '<', '<=', '>', '>=']:
            return BaseType.BOOLEAN
            
        # Logical operators
        elif operator in ['dan', 'atau']:
            return BaseType.BOOLEAN
        
        return BaseType.VOID

    def check_duplicate_identifier(self, name: str, token: Token = None):
        existing_idx = self.symbol_table.find_identifier(name)
        if existing_idx is not None:
            existing_entry = self.symbol_table.tab[existing_idx]
            if existing_entry["lev"] == self.symbol_table.level:
                self.error(f"Duplicate identifier '{name}'", token)
                return True
        return False

    def check_constant_assignment(self, target: ASTNode, token: Token = None):
        if (hasattr(target, 'tab_index') and target.tab_index >= 0 and 
            target.tab_index < len(self.symbol_table.tab)):
            target_entry = self.symbol_table.tab[target.tab_index]
            if target_entry["obj"] == ObjType.CONSTANT:
                self.error(f"Cannot assign to constant '{target.identifier if hasattr(target, 'identifier') else 'unknown'}'", token)
                return False
        return True

    def check_parameter_count(self, func_name: str, expected_count: int, actual_count: int, token: Token = None):
        if expected_count != actual_count:
            self.error(f"Parameter count mismatch in {func_name}: expected {expected_count}, got {actual_count}", token)
            return False
        return True
    
    def validate_parameters(self, func_name: str, param_count: int, param_types: List[BaseType], 
                        token: Token = None) -> bool:
        # Look up function di symbol table
        func_idx = self.symbol_table.find_identifier(func_name)
        if func_idx is None:
            self.error(f"Undefined function/procedure '{func_name}'", token)
            return False
        
        func_entry = self.symbol_table.tab[func_idx]
        
        if func_entry["obj"] not in [ObjType.FUNCTION, ObjType.PROCEDURE]:
            self.error(f"'{func_name}' is not a function or procedure", token)
            return False
        
        if func_name in ['writeln', 'readln', 'write', 'read']:
            return True
        
        func_block_idx = func_entry.get("block_index", -1)
        if func_block_idx < 0 or func_block_idx >= len(self.symbol_table.btab):
            self.error(f"Cannot find parameter information for '{func_name}'", token)
            return False
        
        # Mengambil parameter fungsi
        expected_params = []
        current_idx = self.symbol_table.btab[func_block_idx]["last"]
        
        while current_idx >= self.symbol_table.user_id_start:
            if current_idx < len(self.symbol_table.tab) and self.symbol_table.tab[current_idx] is not None:
                entry = self.symbol_table.tab[current_idx]
                if entry["obj"] == ObjType.VARIABLE and entry.get("is_param", False):
                    expected_params.append({
                        "type": BaseType(entry["type"]),
                        "name": entry["name"]
                    })
            if current_idx < len(self.symbol_table.tab) and self.symbol_table.tab[current_idx]:
                current_idx = self.symbol_table.tab[current_idx]["link"]
            else:
                break
        
        expected_params.reverse()
        
        # Cek jumlah parameter
        if len(expected_params) != param_count:
            self.error(f"Parameter count mismatch in {func_name}: expected {len(expected_params)}, got {param_count}", token)
            return False
        
        # Cek tipe parameter
        for i, (expected, actual) in enumerate(zip(expected_params, param_types)):
            if not self.is_type_compatible(expected["type"], actual):
                self.error(f"Parameter type mismatch in {func_name}: parameter {i+1} ({expected['name']}) expects {expected['type'].name.lower()}, got {actual.name.lower()}", token)
                return False
        
        return True

    def check_array_bounds(self, array_idx: int, index_expr: ASTNode, token: Token = None):
        if array_idx < 0 or array_idx >= len(self.symbol_table.atab):
            return
            
        array_info = self.symbol_table.atab[array_idx]
        
        # Cek jika lower bound > upper bound
        if array_info["low"] > array_info["high"]:
            self.error(f"Invalid array bounds: lower bound ({array_info['low']}) > upper bound ({array_info['high']})", token)
            return
        
        if hasattr(index_expr, 'value') and isinstance(index_expr.value, (int, float)):
            index_value = int(index_expr.value)
            if index_value < array_info["low"] or index_value > array_info["high"]:
                self.error(f"Array index out of bounds: {index_value} not in range {array_info['low']}..{array_info['high']}", token)

    def validate_variable_initialization(self):
        pass

    def visit(self, node: ParseNode) -> ASTNode:
        method_name = f'visit_{node.name.replace("<", "").replace(">", "").replace("-", "_")}'
        method = getattr(self, method_name, self.visit_default)
        
        try:
            return method(node)
        except Exception as e:
            print(f"Warning: Error in {method_name}: {e}")
            ast_node = ASTNode(node.name)
            for child in node.children:
                try:
                    ast_node.add_child(self.visit(child))
                except:
                    continue
            return ast_node
    
    def visit_default(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode(node.name)
        for child in node.children:
            ast_node.add_child(self.visit(child))
        return ast_node
    
    def visit_program(self, node: ParseNode) -> ASTNode:
        # Get program name
        program_name = "Unknown"
        if node.children and node.children[0].name == "<program-header>":
            header_children = node.children[0].children
            if len(header_children) > 1 and header_children[1].token:
                program_name = header_children[1].token.value
        
        # Masukkan program ke symbol table
        program_idx = self.symbol_table.enter_identifier(
            program_name, ObjType.PROGRAM, BaseType.VOID.value
        )
        
        ast_node = ProgramNode("Program", name=program_name, 
                            token=node.children[0].children[1].token if node.children else None,
                            data_type=BaseType.VOID, tab_index=program_idx)
        
        for child in node.children:
            if child.name == "<declaration-part>":
                decl_ast = self.visit(child)
                ast_node.add_child(decl_ast)
            elif child.name == "<compound-statement>":
                main_block_idx = self.symbol_table.enter_block()
                compound_ast = self.visit(child)
                compound_ast.block_index = main_block_idx
                ast_node.add_child(compound_ast)
                self.symbol_table.leave_block()
        
        return ast_node
    
    def visit_declaration_part(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("Declarations")
        for child in node.children:
            if child.name == "<var-declaration>":
                var_decl_ast = self.visit(child)
                # Extract VarDecl nodes langsung
                for var_decl_child in var_decl_ast.children:
                    if isinstance(var_decl_child, VarDeclNode):
                        var_decl_child.block_index = 0  # Set level untuk global variables
                        ast_node.add_child(var_decl_child)
            elif child.name == "<const-declaration>":
                const_decl_ast = self.visit(child)
                # Process constant declarations
                for const_child in const_decl_ast.children:
                    ast_node.add_child(const_child)
            elif child.name == "<type-declaration>":
                type_decl_ast = self.visit(child)
                # Process type declarations  
                for type_child in type_decl_ast.children:
                    ast_node.add_child(type_child)
            elif child.name == "<subprogram-declaration>":  # TAMBAHKAN INI
                subprogram_ast = self.visit(child)
                if subprogram_ast:
                    ast_node.add_child(subprogram_ast)
        return ast_node
    
    def visit_subprogram_declaration(self, node: ParseNode) -> ASTNode:
        if node.children:
            return self.visit(node.children[0])
        return ASTNode("SubprogramDeclaration")
    
    def visit_procedure_declaration(self, node: ParseNode) -> ASTNode:
        proc_name = ""
        
        # Extract procedure name
        for child in node.children:
            if child.name == "IDENTIFIER" and child.token:
                proc_name = child.token.value
                break
        
        if not proc_name:
            return ASTNode("ProcedureDeclaration")
        
        # Cek identifier duplikat
        if self.check_duplicate_identifier(proc_name, 
            node.children[1].token if len(node.children) > 1 else None):
            return ASTNode("ProcedureDeclaration")
        
        # Masukkan procedure ke symbol table
        proc_idx = self.symbol_table.enter_identifier(
            proc_name, ObjType.PROCEDURE, BaseType.VOID.value
        )
        
        # Create procedure node
        proc_node = ASTNode("ProcedureDeclaration", 
                        data_type=BaseType.VOID, tab_index=proc_idx)
        proc_node.procedure_name = proc_name
        
        # Enter procedure block
        proc_block_idx = self.symbol_table.enter_block()
        
        # Simpan block index dalam symbol table entry
        if proc_idx < len(self.symbol_table.tab) and self.symbol_table.tab[proc_idx] is not None:
            self.symbol_table.tab[proc_idx]["block_index"] = proc_block_idx
        
        # Process parameters
        has_params = False
        for child in node.children:
            if child.name == "<formal-parameter-list>":
                param_ast = self.visit(child)
                proc_node.add_child(param_ast)
                has_params = True
                break
        
        # Process procedure body (block)
        for child in node.children:
            if child.name == "<block>":
                block_ast = self.visit(child)
                block_ast.block_index = proc_block_idx
                proc_node.add_child(block_ast)
                break
        
        self.symbol_table.leave_block()
        
        return proc_node

    def visit_function_declaration(self, node: ParseNode) -> ASTNode:
        func_name = ""
        return_type = BaseType.VOID
        
        # Extract function name dan return type
        for i, child in enumerate(node.children):
            if child.name == "IDENTIFIER" and child.token:
                func_name = child.token.value
            elif child.name == "<type>":
                type_ast = self.visit(child)
                return_type = type_ast.data_type if type_ast.data_type else BaseType.VOID
        
        if not func_name:
            return ASTNode("FunctionDeclaration")
        
        # Cek identifier duplikat
        if self.check_duplicate_identifier(func_name, 
            node.children[1].token if len(node.children) > 1 else None):
            return ASTNode("FunctionDeclaration")
        
        # Masukkan function ke symbol table
        func_idx = self.symbol_table.enter_identifier(
            func_name, ObjType.FUNCTION, return_type.value
        )
        
        # Create function node
        func_node = ASTNode("FunctionDeclaration", 
                        data_type=return_type, tab_index=func_idx)
        func_node.function_name = func_name
        
        # Enter function block
        func_block_idx = self.symbol_table.enter_block()
        
        # Simpan block index dalam symbol table entry
        if func_idx < len(self.symbol_table.tab) and self.symbol_table.tab[func_idx] is not None:
            self.symbol_table.tab[func_idx]["block_index"] = func_block_idx
        
        # Process parameters
        has_params = False
        for child in node.children:
            if child.name == "<formal-parameter-list>":
                param_ast = self.visit(child)
                func_node.add_child(param_ast)
                has_params = True
                break
        
        # Process function body (block)
        for child in node.children:
            if child.name == "<block>":
                block_ast = self.visit(child)
                block_ast.block_index = func_block_idx
                func_node.add_child(block_ast)
                break
        
        # Leave function block
        self.symbol_table.leave_block()
        
        return func_node
    
    def visit_function_call(self, node: ParseNode) -> ASTNode:
        func_name = ""
        
        # Extract nama function
        for child in node.children:
            if child.name == "IDENTIFIER" and child.token:
                func_name = child.token.value
                break
        
        if not func_name:
            return ASTNode("FunctionCall", data_type=BaseType.VOID)
        
        # Cari function di symbol table
        func_idx = self.symbol_table.find_identifier(func_name)
        return_type = BaseType.VOID
        
        if func_idx is not None:
            func_entry = self.symbol_table.tab[func_idx]
            if func_entry["obj"] == ObjType.FUNCTION:
                return_type = BaseType(func_entry["type"])
        
        # Kumpulkan parameter
        param_nodes = []
        param_types = []
        
        for child in node.children:
            if child.name == "<parameter-list>":
                param_ast = self.visit(child)
                # Extract parameter expressions dan types
                for param_expr in param_ast.children:
                    param_nodes.append(param_expr)
                    if hasattr(param_expr, 'data_type'):
                        param_types.append(param_expr.data_type)
                    else:
                        param_types.append(BaseType.VOID)
        
        # Validasi parameter untuk user-defined functions
        if func_name not in ['writeln', 'readln', 'write', 'read']:
            self.validate_parameters(func_name, len(param_types), param_types,
                                node.children[0].token if node.children else None)
        
        # Buat function call node
        ast_node = ASTNode("FunctionCall", data_type=return_type, tab_index=func_idx)
        ast_node.function_name = func_name
        
        # Tambahkan parameter
        for param_node in param_nodes:
            ast_node.add_child(param_node)
        
        return ast_node
    
    def visit_formal_parameter_list(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("FormalParameterList")
        for child in node.children:
            if child.name == "<parameter-group>":
                param_group_ast = self.visit(child)
                if param_group_ast:
                    ast_node.add_child(param_group_ast)
        
        # Simpan informasi bahwa current block memiliki parameter
        current_block_idx = self.symbol_table.display[-1]
        if current_block_idx < len(self.symbol_table.btab):
            # Hitung jumlah parameter
            param_count = sum(len(group.children) for group in ast_node.children)
            self.symbol_table.btab[current_block_idx]["param_count"] = param_count
        
        return ast_node
    
    def visit_parameter_group(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("ParameterGroup")
        identifiers = []
        param_type = BaseType.VOID
        
        for child in node.children:
            if child.name == "<identifier-list>":
                identifiers = self.extract_identifiers(child)
            elif child.name == "<type>":
                type_ast = self.visit(child)
                param_type = type_ast.data_type if type_ast.data_type else BaseType.VOID
        
        # Masukkan parameter ke symbol table dengan flag is_param
        for identifier in identifiers:
            param_idx = self.symbol_table.enter_identifier(
                identifier, ObjType.VARIABLE, param_type.value, size=1
            )
            # Tandai sebagai parameter
            if param_idx < len(self.symbol_table.tab) and self.symbol_table.tab[param_idx] is not None:
                self.symbol_table.tab[param_idx]["is_param"] = True
            
            param_node = VarDeclNode("Parameter", identifier=identifier,
                                data_type=param_type, tab_index=param_idx, 
                                block_index=self.symbol_table.display[-1])
            ast_node.add_child(param_node)
        
        return ast_node
            
    def visit_const_declaration(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("ConstDeclaration")
        for child in node.children:
            if child.name == "<const-item>":
                const_item_ast = self.visit(child)
                if const_item_ast:
                    ast_node.add_child(const_item_ast)
        return ast_node
    
    def visit_const_item(self, node: ParseNode) -> ASTNode:
        identifier = None
        value_node = None
        const_value = None
        
        for child in node.children:
            if child.name == "IDENTIFIER" and child.token:
                identifier = child.token.value
            elif child.name == "<const-value>":
                value_node = self.visit(child)
                if hasattr(value_node, 'value'):
                    const_value = value_node.value
                elif value_node.children and hasattr(value_node.children[0], 'value'):
                    const_value = value_node.children[0].value
        
        if identifier and value_node:
            # Cek identifier duplikat
            if self.check_duplicate_identifier(identifier, node.children[0].token if node.children else None):
                const_node = ASTNode("ConstItem", 
                                token=node.children[0].token if node.children else None,
                                data_type=value_node.data_type, tab_index=-1)
                const_node.add_child(value_node)
                return const_node
                
            # Tentukan tipe constant dari value
            const_type = value_node.data_type
            
            # Masukkan constant ke symbol table dengan nilainya
            const_idx = self.symbol_table.enter_identifier(
                identifier, ObjType.CONSTANT, const_type.value, const_value=const_value
            )
            
            # Buat constant node khusus
            const_node = ASTNode("ConstItem", 
                            token=node.children[0].token if node.children else None,
                            data_type=const_type, tab_index=const_idx)
            const_node.add_child(value_node)
            return const_node
        
        return ASTNode("ConstItem")
    
    def visit_const_value(self, node: ParseNode) -> ASTNode:
        if node.children:
            child = node.children[0]
            if child.token:
                token_type = child.token.type
                token_value = child.token.value
                
                # Deteksi char literal
                if token_type == TokenType.STRING_LITERAL:
                    # Cek jika ini char literal (panjang 3, diapit ')
                    if len(token_value) == 3 and token_value.startswith("'") and token_value.endswith("'"):
                        data_type = BaseType.CHAR
                        ast_node = ASTNode("ConstValue", token=child.token, data_type=data_type)
                        ast_node.value = token_value[1]
                        return ast_node
                    else:
                        # String literal biasa
                        data_type = BaseType.STRING
                        ast_node = ASTNode("ConstValue", token=child.token, data_type=data_type)
                        ast_node.value = token_value
                        return ast_node
                        
                elif token_type == TokenType.NUMBER:
                    # Tentukan integer atau real
                    if '.' in token_value:
                        data_type = BaseType.REAL
                        value = float(token_value)
                    else:
                        data_type = BaseType.INTEGER
                        value = int(token_value)
                    ast_node = ASTNode("ConstValue", token=child.token, data_type=data_type)
                    ast_node.value = value
                    return ast_node
                    
                elif token_type == TokenType.CHAR_LITERAL:
                    data_type = BaseType.CHAR
                    ast_node = ASTNode("ConstValue", token=child.token, data_type=data_type)
                    ast_node.value = token_value
                    return ast_node
                    
                elif token_type == TokenType.IDENTIFIER:
                    # Cari identifier di symbol table
                    ident_idx = self.symbol_table.find_identifier(token_value)
                    if ident_idx is not None:
                        ident_entry = self.symbol_table.tab[ident_idx]
                        data_type = BaseType(ident_entry["type"])
                        ast_node = ASTNode("ConstValue", token=child.token, data_type=data_type)
                        # Untuk identifier constants, resolve value nanti
                        ast_node.value = token_value
                        return ast_node
                    else:
                        data_type = BaseType.VOID
                        self.error(f"Undefined identifier '{token_value}'", child.token)
                else:
                    data_type = BaseType.VOID
            
        return ASTNode("ConstValue", data_type=BaseType.VOID)
    
    def visit_var_declaration(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("VarDeclaration")
        for child in node.children:
            if child.name == "<var-item>":
                var_item_ast = self.visit(child)
                # Tambahkan semua children dari VarItem (yang sudah berupa VarDecl nodes)
                for var_decl in var_item_ast.children:
                    ast_node.add_child(var_decl)
        return ast_node
    
    def visit_var_item(self, node: ParseNode) -> ASTNode:
        identifiers = []
        type_node = None
        type_ast = None
        
        for child in node.children:
            if child.name == "<identifier-list>":
                identifiers = self.extract_identifiers(child)
            elif child.name == "<type>":
                type_node = child
                type_ast = self.visit(child)
        
        if identifiers and type_ast:
            base_type = type_ast.data_type
            
            # Buat parent node
            var_ast = ASTNode("VarItem")
            
            # Masukkan setiap identifier ke symbol table dan buat VarDeclNode
            for identifier in identifiers:
                # Cek duplicate identifier
                if not self.check_duplicate_identifier(identifier, 
                    node.children[0].children[0].token if node.children and node.children[0].children else None):
                    
                    var_idx = self.symbol_table.enter_identifier(
                        identifier, ObjType.VARIABLE, base_type.value, size=1
                    )
                    # Buat VarDeclNode dengan level yang benar
                    ident_ast = VarDeclNode("Variable", identifier=identifier,
                                        token=Token(TokenType.IDENTIFIER, identifier, 0, 0),
                                        data_type=base_type, tab_index=var_idx, block_index=0)
                    var_ast.add_child(ident_ast)
                else:
                    # Tetap buat node tapi tandai sebagai error
                    ident_ast = VarDeclNode("Variable", identifier=identifier,
                                        token=Token(TokenType.IDENTIFIER, identifier, 0, 0),
                                        data_type=base_type, tab_index=-1, block_index=0)
                    var_ast.add_child(ident_ast)
            
            return var_ast
        
        return ASTNode("VarItem")
    
    def visit_type(self, node: ParseNode) -> ASTNode:
        if not node.children:
            return ASTNode("Type", data_type=BaseType.VOID)
            
        first_child = node.children[0]
        
        # Handle built-in types
        if first_child.token:
            token_value = first_child.token.value.lower()
            if token_value == "integer":
                return ASTNode("Type", data_type=BaseType.INTEGER)
            elif token_value == "real":
                return ASTNode("Type", data_type=BaseType.REAL)
            elif token_value == "boolean":
                return ASTNode("Type", data_type=BaseType.BOOLEAN)
            elif token_value == "char":
                return ASTNode("Type", data_type=BaseType.CHAR)
            elif token_value == "string":
                return ASTNode("Type", data_type=BaseType.STRING)
        
        # Handle array type
        if first_child.name == "<array-type>":
            return self.visit_array_type(first_child)
            
        # Handle range type (direct range seperti 1..10)
        if first_child.name == "<range>":
            # Treat range sebagai integer type untuk sekarang
            return ASTNode("Type", data_type=BaseType.INTEGER)
            
        # Handle type alias (identifier)
        if first_child.name == "IDENTIFIER" and first_child.token:
            # Cari type di symbol table
            type_name = first_child.token.value
            type_idx = self.symbol_table.find_identifier(type_name)
            if type_idx is not None and self.symbol_table.tab[type_idx]["obj"] == ObjType.TYPE:
                base_type = BaseType(self.symbol_table.tab[type_idx]["type"])
                return ASTNode("Type", data_type=base_type, tab_index=type_idx)
            else:
                self.error(f"Undefined type '{type_name}'", first_child.token)
        
        return ASTNode("Type", data_type=BaseType.VOID)
    
    def visit_array_type(self, node: ParseNode) -> ASTNode:
        # Extract index specification dan element type
        index_spec = None
        element_type_node = None
        low_bound = 1  # default
        high_bound = 10  # default
        
        for child in node.children:
            if child.name == "<index-specification>":
                index_spec = child
                # Parse range
                range_result = self.parse_range(index_spec)
                if range_result:
                    low_bound, high_bound = range_result
            elif child.name == "<type>":
                element_type_node = self.visit(child)
        
        if element_type_node:
            # Cek invalid array bounds
            if low_bound > high_bound:
                self.error(f"Invalid array bounds: {low_bound}..{high_bound} (lower bound > upper bound)", 
                        node.children[0].token if node.children else None)
            
            # Buat array table entry
            array_idx = self.symbol_table.enter_array(
                BaseType.INTEGER.value,  # index type (asumsi integer untuk sekarang)
                element_type_node.data_type.value,  # element type
                low_bound,  
                high_bound,
                1   # element size
            )
            
            return ASTNode("ArrayType", data_type=BaseType.ARRAY, tab_index=array_idx)
        
        return ASTNode("ArrayType", data_type=BaseType.ARRAY)
    
    def visit_type_declaration(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("TypeDeclaration")
        for child in node.children:
            if child.name == "<type-item>":
                type_item_ast = self.visit(child)
                if type_item_ast:
                    ast_node.add_child(type_item_ast)
        return ast_node

    def visit_type_item(self, node: ParseNode) -> ASTNode:
        identifier = None
        type_def_ast = None
        
        for child in node.children:
            if child.name == "IDENTIFIER" and child.token:
                identifier = child.token.value
            elif child.name == "<type-definition>":
                type_def_node = child
                # Handle different type definitions
                if type_def_node.children:
                    first_child = type_def_node.children[0]
                    if first_child.name == "<type>":
                        type_def_ast = self.visit(first_child)
                    elif first_child.name == "<range>":
                        # Untuk range types seperti "1..10", treat sebagai integer type
                        type_def_ast = ASTNode("RangeType", data_type=BaseType.INTEGER)
                    elif first_child.name == "<array-type>":
                        type_def_ast = self.visit(first_child)
                    else:
                        # Default case
                        type_def_ast = self.visit(first_child)
                else:
                    type_def_ast = ASTNode("TypeDefinition", data_type=BaseType.VOID)
        
        if identifier and type_def_ast:
            # Masukkan type alias ke symbol table
            type_idx = self.symbol_table.enter_identifier(
                identifier, ObjType.TYPE, type_def_ast.data_type.value if type_def_ast.data_type else BaseType.VOID.value
            )
            
            # Buat specialized type node
            type_node = ASTNode("TypeItem", 
                            token=node.children[0].token if node.children else None,
                            data_type=type_def_ast.data_type, tab_index=type_idx)
            type_node.add_child(type_def_ast)
            return type_node
        
        return ASTNode("TypeItem", data_type=BaseType.VOID)
    
    def visit_type_definition(self, node: ParseNode) -> ASTNode:
        if node.children:
            return self.visit(node.children[0])
        return ASTNode("TypeDefinition", data_type=BaseType.VOID)
    
    def visit_compound_statement(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("CompoundStatement", block_index=self.symbol_table.display[-1])
        for child in node.children:
            if child.name == "<statement-list>":
                stmt_list = self.visit(child)
                # Extract statements langsung
                for stmt in stmt_list.children:
                    ast_node.add_child(stmt)
        return ast_node
    
    def visit_statement_list(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("StatementList")
        for child in node.children:
            if (child.name == "<statement>" or 
                child.name == "<assignment-statement>" or
                child.name == "<procedure-call>"):
                stmt_ast = self.visit(child)
                if stmt_ast:  # Hanya tambahkan jika tidak None
                    ast_node.add_child(stmt_ast)
        return ast_node
    
    def visit_statement(self, node: ParseNode) -> ASTNode:
        if node.children:
            return self.visit(node.children[0])
        return ASTNode("Statement", data_type=BaseType.VOID)
    
    def visit_assignment_statement(self, node: ParseNode) -> ASTNode:
        target_node = None
        value_node = None
        
        # Pattern: <variable> - ASSIGN_OPERATOR - <expression>
        for i in range(len(node.children) - 2):
            if (node.children[i].name == "<variable>" and 
                node.children[i + 1].name == "ASSIGN_OPERATOR" and 
                node.children[i + 2].name == "<expression>"):
                
                target_child = node.children[i]
                value_child = node.children[i + 2]
                
                try:
                    target_node = self.visit(target_child)
                    value_node = self.visit(value_child)
                    
                    # Cek constant assignment
                    if target_node:
                        self.check_constant_assignment(target_node, 
                            node.children[i + 1].token if i + 1 < len(node.children) else None)
                    break
                except Exception as e:
                    print(f"Warning: Error processing assignment: {e}")
                    continue
                
        if not target_node or not value_node:
            # Fallback approach
            variables = []
            expressions = []
            
            for child in node.children:
                if child.name == "<variable>":
                    try:
                        var_node = self.visit(child)
                        variables.append(var_node)
                    except:
                        continue
                elif child.name == "<expression>":
                    try:
                        expr_node = self.visit(child)
                        expressions.append(expr_node)
                    except:
                        continue
            
            if variables and expressions:
                target_node = variables[0]
                value_node = expressions[0]
                
                # Cek constant assignment
                if target_node:
                    self.check_constant_assignment(target_node, 
                        node.children[1].token if len(node.children) > 1 else None)
        
        # Type checking - hanya jika kedua node berhasil diproses
        if target_node and value_node and target_node.data_type and value_node.data_type:
            # Cek jika target adalah array element
            if hasattr(target_node, 'is_array_element') and target_node.is_array_element:
                if not self.is_type_compatible(target_node.data_type, value_node.data_type):
                    self.error(f"Type mismatch in array assignment: cannot assign {value_node.data_type.name} to array element of type {target_node.data_type.name}", 
                            node.children[1].token if len(node.children) > 1 else None)
            else:
                if not self.is_type_compatible(target_node.data_type, value_node.data_type):
                    self.error(f"Type mismatch in assignment: cannot assign {value_node.data_type.name} to {target_node.data_type.name}", 
                            node.children[1].token if len(node.children) > 1 else None)
        
        # Buat AssignmentNode
        ast_node = AssignmentNode("Assignment", data_type=BaseType.VOID)
        if target_node:
            ast_node.add_child(target_node)
        else:
            ast_node.add_child(ASTNode("UnknownTarget"))
        
        if value_node:
            ast_node.add_child(value_node)
        else:
            ast_node.add_child(ASTNode("UnknownValue"))
                    
        return ast_node
    
    def visit_expression(self, node: ParseNode) -> ASTNode:
        if len(node.children) == 1:
            # Simple expression saja
            return self.visit(node.children[0])
        else:
            # Expression dengan operator
            left_expr = self.visit(node.children[0])
            
            # Jika hanya ada 1 child setelah left_expr, return left_expr saja
            if len(node.children) == 1:
                return left_expr
                
            operator_node = node.children[1]
            right_expr = self.visit(node.children[2])
            
            # Tentukan nilai operator
            operator_value = ""
            if operator_node.children and operator_node.children[0].token:
                operator_value = operator_node.children[0].token.value
            elif operator_node.token:
                operator_value = operator_node.token.value
            
            # Tentukan result type
            result_type = self.get_expression_type(left_expr.data_type, right_expr.data_type, operator_value)
            
            # Gunakan BinaryExpressionNode khusus dengan 2 children
            ast_node = BinaryExpressionNode("BinaryExpression", data_type=result_type, operator=operator_value)
            ast_node.add_child(left_expr)
            ast_node.add_child(right_expr)  # Hanya 2 children: left dan right
            return ast_node
        
    def visit_simple_expression(self, node: ParseNode) -> ASTNode:
        if len(node.children) == 1:
            return self.visit(node.children[0])
        else:
            # Simple expression dengan additive operators
            left_term = self.visit(node.children[0])
            result_node = left_term
            
            # Handle multiple terms - gunakan while loop yang lebih aman
            i = 1
            while i < len(node.children):
                # Pastikan ada cukup children untuk operator dan term
                if i + 1 >= len(node.children):
                    break
                    
                operator_node = node.children[i]
                right_term = self.visit(node.children[i + 1])
                
                # Tentukan nilai operator
                operator_value = ""
                if operator_node.children and operator_node.children[0].token:
                    operator_value = operator_node.children[0].token.value
                elif operator_node.token:
                    operator_value = operator_node.token.value
                
                # Tentukan result type
                result_type = self.get_expression_type(
                    result_node.data_type, right_term.data_type, operator_value
                )
                
                # Buat binary expression dengan 2 children
                new_result = BinaryExpressionNode("BinaryExpression", data_type=result_type, operator=operator_value)
                new_result.add_child(result_node)
                new_result.add_child(right_term)  # Hanya 2 children
                result_node = new_result
                i += 2
            
            return result_node
    
    def visit_term(self, node: ParseNode) -> ASTNode:
        if len(node.children) == 1:
            return self.visit(node.children[0])
        else:
            # Term dengan multiplicative operators
            left_factor = self.visit(node.children[0])
            result_node = left_factor
            
            # Handle multiple factors - gunakan while loop yang lebih aman
            i = 1
            while i < len(node.children):
                # Pastikan ada cukup children untuk operator dan factor
                if i + 1 >= len(node.children):
                    break
                    
                operator_node = node.children[i]
                right_factor = self.visit(node.children[i + 1])
                
                # Tentukan nilai operator
                operator_value = ""
                if operator_node.children and operator_node.children[0].token:
                    operator_value = operator_node.children[0].token.value
                elif operator_node.token:
                    operator_value = operator_node.token.value
                
                # Tentukan result type
                result_type = self.get_expression_type(
                    result_node.data_type, right_factor.data_type, operator_value
                )
                
                # Buat binary expression dengan 2 children
                new_result = BinaryExpressionNode("BinaryExpression", data_type=result_type, operator=operator_value)
                new_result.add_child(result_node)
                new_result.add_child(right_factor)  # Hanya 2 children
                result_node = new_result
                i += 2
            
            return result_node
    
    def visit_factor(self, node: ParseNode) -> ASTNode:
        if not node.children:
            return ASTNode("Factor", data_type=BaseType.VOID)
        
        first_child = node.children[0]
        
        # Boolean literals
        if first_child.name == "IDENTIFIER" and first_child.token:
            ident_name = first_child.token.value.lower()
            if ident_name in ['benar', 'salah']:
                # Treat sebagai boolean literal
                data_type = BaseType.BOOLEAN
                value = ident_name == 'benar'
                ast_node = BooleanNode("Boolean", token=first_child.token, data_type=data_type)
                ast_node.value = value
                ast_node.identifier = ident_name
                return ast_node
        
        # Number literal
        if first_child.name == "NUMBER" and first_child.token:
            if '.' in first_child.token.value:
                data_type = BaseType.REAL
                try:
                    value = float(first_child.token.value)
                except ValueError:
                    value = 0.0
            else:
                data_type = BaseType.INTEGER
                try:
                    value = int(first_child.token.value)
                except ValueError:
                    value = 0
            return NumberNode("Number", token=first_child.token, data_type=data_type, value=value)
        
        # String literal - Deteksi char vs string
        elif first_child.name == "STRING_LITERAL" and first_child.token:
            token_value = first_child.token.value
            # Deteksi char literal: string dengan panjang 3 dan diapit tanda kutip tunggal
            if len(token_value) == 3 and token_value.startswith("'") and token_value.endswith("'"):
                data_type = BaseType.CHAR
                ast_node = ASTNode("Char", token=first_child.token, data_type=data_type)
                ast_node.value = token_value[1]  # Extract char
                return ast_node
            else:
                # String literal biasa
                return StringNode("String", token=first_child.token, data_type=BaseType.STRING, value=token_value)
        
        # Char literal (jika ada token type khusus)
        elif first_child.name == "CHAR_LITERAL" and first_child.token:
            return ASTNode("Char", token=first_child.token, data_type=BaseType.CHAR)
        
        # Identifier (variable or function call)
        elif first_child.name == "IDENTIFIER" and first_child.token:
            ident_name = first_child.token.value
            ident_idx = self.symbol_table.find_identifier(ident_name)
            
            if ident_idx is not None:
                ident_entry = self.symbol_table.tab[ident_idx]
                ident_type = BaseType(ident_entry["type"])
                obj_type = ident_entry["obj"]
                
                if obj_type == ObjType.CONSTANT:
                    # Handle constant identifier
                    const_value = self.symbol_table.get_constant_value(ident_name)
                    ast_node = ASTNode("ConstIdentifier", token=first_child.token, 
                                data_type=ident_type, tab_index=ident_idx)
                    ast_node.value = const_value
                    ast_node.identifier = ident_name
                    return ast_node
                else:
                    # Regular variable
                    return VariableNode("Variable", token=first_child.token, 
                                data_type=ident_type, tab_index=ident_idx, identifier=ident_name)
            else:
                self.error(f"Undefined identifier '{ident_name}'", first_child.token)
                return VariableNode("Variable", token=first_child.token, 
                            data_type=BaseType.VOID, identifier=ident_name)
        
        # Parenthesized expression
        elif (first_child.name == "LPARENTHESIS" and first_child.token and
            len(node.children) > 2 and node.children[2].name == "<expression>"):
            return self.visit(node.children[1])
        
        # Function call
        elif first_child.name == "<function-call>":
            return self.visit(first_child)
        
        # Handle case LOGICAL_OPERATOR(tidak) <factor>
        elif (first_child.name == "LOGICAL_OPERATOR(tidak)" and first_child.token and
            len(node.children) > 1):
            # Ini NOT operator
            factor_node = self.visit(node.children[1])
            ast_node = ASTNode("NotExpression", data_type=BaseType.BOOLEAN)
            ast_node.add_child(factor_node)
            return ast_node
        
        return ASTNode("Factor", data_type=BaseType.VOID)
    
    def visit_variable(self, node: ParseNode) -> ASTNode:
        # Cek pattern array access: IDENTIFIER LBRACKET expression (COMMA expression)* RBRACKET
        if (len(node.children) >= 4 and
            node.children[0].name == "IDENTIFIER" and
            node.children[1].name == "LBRACKET"):
            
            # Ini array access - cari RBRACKET
            rbrace_index = -1
            for i in range(2, len(node.children)):
                if node.children[i].name == "RBRACKET":
                    rbrace_index = i
                    break
            
            if rbrace_index > 2:  # Ada expression di antara LBRACKET dan RBRACKET
                array_name = node.children[0].token.value
                array_idx = self.symbol_table.find_identifier(array_name)
                
                if array_idx is not None:
                    array_entry = self.symbol_table.tab[array_idx]
                    if array_entry["type"] == BaseType.ARRAY.value:
                        # Dapatkan tipe elemen array dari atab
                        array_ref = array_entry["ref"]
                        if array_ref < len(self.symbol_table.atab):
                            element_type = BaseType(self.symbol_table.atab[array_ref]["element_type"])
                            
                            # Parse index expressions untuk bounds checking
                            index_expressions = []
                            i = 2
                            while i < rbrace_index:
                                if node.children[i].name == "<expression>":
                                    index_expr = self.visit(node.children[i])
                                    index_expressions.append(index_expr)
                                    # Check array bounds untuk setiap index
                                    self.check_array_bounds(array_ref, index_expr, node.children[1].token)
                                elif node.children[i].name == "COMMA":
                                    # Skip comma, lanjut ke expression berikutnya
                                    pass
                                i += 1
                            
                            # Buat node untuk array element access dengan tipe ELEMENT
                            var_node = VariableNode("ArrayElement", identifier=array_name,
                                            token=node.children[0].token, 
                                            data_type=element_type, tab_index=array_idx)
                            var_node.is_array_element = True
                            var_node.index_expressions = index_expressions  # Simpan index expressions
                            return var_node
                
                # Jika bukan array atau tidak ditemukan, treat sebagai error
                self.error(f"'{array_name}' is not an array or undefined", node.children[0].token)
                return VariableNode("Variable", identifier=array_name,
                                token=node.children[0].token, 
                                data_type=BaseType.VOID)
        
        # Untuk kasus sederhana (non-array)
        for child in node.children:
            if child.name == "IDENTIFIER" and child.token:
                var_name = child.token.value
                var_idx = self.symbol_table.find_identifier(var_name)
                
                if var_idx is not None:
                    var_type = BaseType(self.symbol_table.tab[var_idx]["type"])
                    return VariableNode("Variable", identifier=var_name,
                                    token=child.token, 
                                    data_type=var_type, tab_index=var_idx)
                else:
                    self.error(f"Undefined variable '{var_name}'", child.token)
                    return VariableNode("Variable", identifier=var_name,
                                    token=child.token, 
                                    data_type=BaseType.VOID)
        
        return ASTNode("UnknownVariable")
    
    def visit_procedure_call(self, node: ParseNode) -> ASTNode:
        proc_name = ""
        for child in node.children:
            if (child.name == "IDENTIFIER" and child.token) or \
            (child.name.startswith("KEYWORD") and child.token and
                child.token.value.lower() in ['writeln', 'readln', 'write', 'read']):
                proc_name = child.token.value
                break
        
        # Buat procedure call node
        ast_node = ProcedureCallNode("ProcedureCall", data_type=BaseType.VOID, procedure_name=proc_name)
        
        # Cari procedure di symbol table
        proc_idx = self.symbol_table.find_identifier(proc_name)
        if proc_idx is not None:
            ast_node.tab_index = proc_idx
            proc_entry = self.symbol_table.tab[proc_idx]
            if proc_entry["obj"] == ObjType.PROCEDURE:
                ast_node.is_user_defined = True
            else:
                ast_node.is_user_defined = False
        else:
            if proc_name in ['writeln', 'readln', 'write', 'read']:
                ast_node.is_user_defined = False
            else:
                self.error(f"Undefined procedure '{proc_name}'", 
                        node.children[0].token if node.children else None)
        
        # Kumpulkan dan validasi parameter untuk user-defined procedures
        param_nodes = []
        param_types = []
        
        for child in node.children:
            if child.name == "<parameter-list>":
                param_ast = self.visit(child)
                # Extract parameter expressions dan types
                for param_expr in param_ast.children:
                    param_nodes.append(param_expr)
                    if hasattr(param_expr, 'data_type'):
                        param_types.append(param_expr.data_type)
                    else:
                        param_types.append(BaseType.VOID)
        
        # Validasi parameter untuk user-defined procedures
        if proc_name not in ['writeln', 'readln', 'write', 'read'] and ast_node.is_user_defined:
            self.validate_parameters(proc_name, len(param_types), param_types,
                                node.children[0].token if node.children else None)
        
        # Tambahkan parameter
        for param_node in param_nodes:
            ast_node.add_child(param_node)
        
        return ast_node
    
    def visit_parameter_list(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("ParameterList")
        for child in node.children:
            if child.name == "<expression>":
                ast_node.add_child(self.visit(child))
        return ast_node
    
    def visit_block(self, node: ParseNode) -> ASTNode:
        ast_node = ASTNode("Block", block_index=self.symbol_table.display[-1])
        
        for child in node.children:
            if child.name == "<declaration-part>":
                decl_ast = self.visit(child)
                ast_node.add_child(decl_ast)
            elif child.name == "<compound-statement>":
                compound_ast = self.visit(child)
                ast_node.add_child(compound_ast)
        
        return ast_node