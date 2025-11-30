program TypeMismatch;
variabel
  x: integer;
  y: real;
  flag: boolean;
  ch: char;
mulai
  x := 10;       { Valid }
  y := 3.14;     { Valid }
  flag := benar; { Valid }
  ch := 'A';     { Valid }
  
  { SEMANTIC ERROR: Type mismatch }
  x := y;        { Error: real tidak bisa diassign ke integer tanpa konversi }
  flag := x;     { Error: integer tidak bisa diassign ke boolean }
  ch := 65;      { Error: integer tidak bisa diassign ke char }
  y := flag;     { Error: boolean tidak bisa diassign ke real }
selesai.