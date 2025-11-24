program ParamMismatch;

fungsi Add(a, b: integer): integer;
mulai
  Add := a + b;
selesai;

prosedur PrintNumber(num: integer);
mulai
  writeln('Number: ', num);
selesai;

variabel
  x: integer;
  y: real;
  flag: boolean;
mulai
  x := Add(5, 10);        { Valid }
  y := Add(3, 4);         { Valid (integer ke real OK) }
  
  { SEMANTIC ERROR: Parameter type mismatch }
  x := Add(5, 3.14);      { Error: real tidak bisa ke integer parameter }
  PrintNumber(y);         { Error: real tidak bisa ke integer parameter }
  PrintNumber(flag);      { Error: boolean tidak bisa ke integer parameter }
  
  { SEMANTIC ERROR: Wrong number of parameters }
  x := Add(5);            { Error: kurang parameter }
  x := Add(1, 2, 3);      { Error: kelebihan parameter }
selesai.