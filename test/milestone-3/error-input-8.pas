program InvalidOps;
variabel
  a, b: integer;
  x, y: real;
  p, q: boolean;
  c1, c2: char;
mulai
  { Valid operations }
  a := 10 + 5;
  x := 3.14 * 2.0;
  p := benar dan salah;
  
  { SEMANTIC ERROR: Invalid operations }
  p := a + b;           { Error: arithmetic on boolean }
  x := p * q;           { Error: arithmetic on boolean }
  a := c1 + c2;         { Error: arithmetic on char }
  p := 10 > 'A';        { Error: comparison between integer dan char }
  q := x dan y;         { Error: logical operation on real }
selesai.