program ScopeTest;
variabel
  global: integer;

prosedur TestProcedure;
variabel
  local: integer;
  global: real;  { SEMANTIC ERROR: Duplicate in different scope? (tergantung implementasi) }
mulai
  local := 10;          { Valid }
  global := 3.14;       { Valid (shadowing) }
  
  { SEMANTIC ERROR: Undefined in this scope }
  x := 5;               { Error: x tidak dideklarasikan di scope ini }
selesai;

fungsi TestFunction: integer;
mulai
  { SEMANTIC ERROR: Cannot access local variable from different scope }
  TestFunction := local;  { Error: local tidak terdefinisi di sini }
selesai;

mulai
  TestProcedure;
  global := 20;         { Valid - mengakses global }
selesai.