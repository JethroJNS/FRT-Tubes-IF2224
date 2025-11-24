program ConstAssignment;
konstanta
  MAX = 100;
  PI = 3.14;
  NAME = 'Test';
variabel
  x: integer;
mulai
  { Valid - menggunakan constant }
  x := MAX;
  
  { SEMANTIC ERROR: Assignment to constant }
  MAX := 200;        { Error: cannot assign to constant }
  PI := 3.14159;     { Error: cannot assign to constant }
  NAME := 'NewName'; { Error: cannot assign to constant }
selesai.