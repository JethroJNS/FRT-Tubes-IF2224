program ReturnMismatch;

fungsi GetInteger: integer;
mulai
  GetInteger := 3.14;   { SEMANTIC ERROR: Return type mismatch }
selesai;

fungsi GetBoolean: boolean;
variabel
  x: integer;
mulai
  x := 10;
  GetBoolean := x;      { SEMANTIC ERROR: Return type mismatch }
selesai;

fungsi NoReturn: integer;  { SEMANTIC ERROR: Function tidak mengembalikan nilai }
variabel
  x: integer;
mulai
  x := 10;
  { Tidak ada assignment ke NoReturn }
selesai;

mulai
  writeln(GetInteger);
  writeln(GetBoolean);
selesai.