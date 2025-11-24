program UndefinedTest;
variabel
  a, b: integer;
mulai
  { SEMANTIC ERROR: Undefined variables }
  x := 10;           { Error: x tidak dideklarasikan }
  result := a + b;   { Error: result tidak dideklarasikan }
  
  { SEMANTIC ERROR: Undefined function }
  c := Calculate(a, b);  { Error: Calculate tidak dideklarasikan }
  
  { SEMANTIC ERROR: Undefined procedure }  
  PrintResult(c);        { Error: PrintResult tidak dideklarasikan }
selesai.