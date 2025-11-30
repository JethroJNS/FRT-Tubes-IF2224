from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass, field
from src.parse_tree import ParseNode
from src.tokens import Token, TokenType

class ObjType(Enum):
    CONSTANT = auto()
    VARIABLE = auto()
    TYPE = auto()
    PROCEDURE = auto()
    FUNCTION = auto()
    PROGRAM = auto()

class BaseType(Enum):
    INTEGER = 1
    REAL = 2
    BOOLEAN = 3
    CHAR = 4
    STRING = 5
    ARRAY = 6
    RECORD = 7
    VOID = 8
    RANGE = 9

class SymbolTable:
    def __init__(self):
        self.tab: List[Dict[str, Any]] = []
        self.btab: List[Dict[str, Any]] = []
        self.atab: List[Dict[str, Any]] = []
        
        # Initialize dengan reserved words (indices 0-28)
        self._init_reserved_words()
        
        self.display: List[int] = []
        self.level: int = -1
        self.next_adr: int = 0
        
        # Counter untuk user identifiers mulai dari 29
        self.user_id_start = 29
        self.next_user_id = 29
        
        # Store constant values
        self.const_values: Dict[str, Any] = {}
        
    def _init_reserved_words(self):
        # Types
        reserved_types = [
            ("integer", BaseType.INTEGER),
            ("real", BaseType.REAL), 
            ("boolean", BaseType.BOOLEAN),
            ("char", BaseType.CHAR),
            ("string", BaseType.STRING)
        ]
        
        # Keywords lainnya
        other_keywords = [
            "program", "variabel", "mulai", "selesai", "jika", "maka", "selainitu",
            "selama", "lakukan", "untuk", "ke", "turunke", "larik", "dari", 
            "prosedur", "fungsi", "konstanta", "tipe", "kasus", "rekaman", 
            "ulangi", "sampai"
        ]
        
        for name, base_type in reserved_types:
            self.tab.append({
                "name": name,
                "obj": ObjType.TYPE,
                "type": base_type.value,
                "ref": 0,        # Pointer ke tabel lain untuk tipe komposit
                "nrm": 1,        # Normal variable (1) atau parameter by-reference (0)
                "lev": 0,        # Level lexical
                "adr": 0,        # Offset/address
                "link": 0        # Link ke identifier sebelumnya dalam block
            })
        
        for name in other_keywords[:23]:
            self.tab.append({
                "name": name,
                "obj": ObjType.TYPE,
                "type": BaseType.VOID.value,
                "ref": 0,
                "nrm": 1,
                "lev": 0,
                "adr": 0,
                "link": len(self.tab) - 1
            })
        
        # Built-in procedures
        built_ins = [
            ("writeln", ObjType.PROCEDURE, BaseType.VOID.value),
            ("readln", ObjType.PROCEDURE, BaseType.VOID.value),
            ("write", ObjType.PROCEDURE, BaseType.VOID.value),
            ("read", ObjType.PROCEDURE, BaseType.VOID.value)
        ]
        
        for name, obj_type, data_type in built_ins:
            self.tab.append({
                "name": name,
                "obj": obj_type,
                "type": data_type,
                "ref": 0,
                "nrm": 1,
                "lev": 0,
                "adr": 0,
                "link": len(self.tab) - 1
            })
    
    def enter_block(self) -> int:
        self.level += 1
        block_index = len(self.btab)
        
        self.btab.append({
            "last": 0,      # Pointer ke identifier terakhir dalam block
            "lpar": 0,      # Pointer ke parameter terakhir (untuk prosedur/fungsi)
            "psze": 0,      # Total ukuran parameter
            "vsze": 0       # Total ukuran variabel lokal
        })
        self.display.append(block_index)
        return block_index
    
    def leave_block(self):
        if self.level > 0:
            self.level -= 1
            self.display.pop()
    
    def enter_identifier(self, name: str, obj_type: ObjType, data_type: int, 
                        ref: int = 0, nrm: int = 1, size: int = 1, const_value: Any = None) -> int:
        # Gunakan next_user_id untuk user-defined identifiers
        tab_index = self.next_user_id
        self.next_user_id += 1
        
        if obj_type == ObjType.VARIABLE:
            adr = self.next_adr
            self.next_adr += size
        else:
            adr = 0

        current_block_idx = self.display[self.level]
        current_block = self.btab[current_block_idx]
        prev_last = current_block["last"]
        
        if tab_index >= len(self.tab):
            while len(self.tab) <= tab_index:
                self.tab.append(None)
        
        # Link menunjuk ke identifier sebelumnya dalam block yang sama
        link_value = prev_last if prev_last >= self.user_id_start else 0
        
        self.tab[tab_index] = {
            "name": name,
            "obj": obj_type,
            "type": data_type,
            "ref": ref,        # Untuk tipe komposit (array/record)
            "nrm": nrm,        # 1 = normal var, 0 = parameter by-reference
            "lev": self.level, # Lexical level
            "adr": adr,        # Address/offset
            "link": link_value # Link ke ident sebelumnya dalam block
        }
        
        # Store constant value
        if obj_type == ObjType.CONSTANT and const_value is not None:
            self.const_values[name] = const_value
        
        # Update last pointer blok
        current_block["last"] = tab_index
        
        # Update block size
        if obj_type == ObjType.VARIABLE:
            current_block["vsze"] += size
            
        return tab_index

    def find_identifier(self, name: str) -> Optional[int]:
        # Search from current level down to global level
        for level in range(self.level, -1, -1):
            block_index = self.display[level]
            last_idx = self.btab[block_index]["last"]
            
            current_idx = last_idx
            while current_idx >= self.user_id_start:
                if (current_idx < len(self.tab) and 
                    self.tab[current_idx] is not None and 
                    self.tab[current_idx]["name"] == name):
                    return current_idx
                current_idx = self.tab[current_idx]["link"] if current_idx < len(self.tab) and self.tab[current_idx] else -1
                
            # Cek reserved words (0-28)
            for i in range(min(29, len(self.tab))):
                if self.tab[i] and self.tab[i]["name"] == name:
                    return i
                    
        return None
    
    def get_constant_value(self, name: str) -> Optional[Any]:
        return self.const_values.get(name)
    
    def enter_array(self, index_type: int, element_type: int, low_bound: int, 
                   high_bound: int, element_size: int = 1) -> int:
        array_size = (high_bound - low_bound + 1) * element_size
        
        atab_index = len(self.atab)
        self.atab.append({
            "index_type": index_type,       # Tipe indeks array
            "element_type": element_type,   # Tipe elemen array  
            "eref": 0,                      # Pointer ke detail tipe elemen jika komposit
            "low": low_bound,               # Batas bawah indeks
            "high": high_bound,             # Batas atas indeks
            "element_size": element_size,   # Ukuran satu elemen
            "size": array_size              # Total ukuran array
        })
        
        return atab_index