program DuplicateTest;
variabel
  x: integer;
  x: real;        { SEMANTIC ERROR: Duplicate identifier }
  y: boolean;
  
fungsi Test(): integer;
mulai
  Test := 1;
selesai;

fungsi Test(): real;  { SEMANTIC ERROR: Duplicate function }
mulai
  Test := 3.14;
selesai;

variabel
  y: char;        { SEMANTIC ERROR: Duplicate identifier }
mulai
  x := 10;
  y := benar;
selesai.