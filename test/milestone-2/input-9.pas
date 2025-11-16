program Input9;

variabel
  a, b, c, d: integer;
  x, y, z: real;
  p, q, r, s: boolean;
  ch1, ch2: char;

fungsi Calculate(a, b: integer; op: char): integer;
mulai
  jika op = '+' maka
    Calculate := a + b
  selainitu jika op = '-' maka
    Calculate := a - b
  selainitu jika op = '*' maka
    Calculate := a * b
  selainitu jika op = '/' maka
    Calculate := a bagi b
  selainitu
    Calculate := 0;
selesai;

prosedur TestBooleanOps(x, y: integer; flag: boolean);
variabel
  result: boolean;
mulai
  result := (x > y) dan flag;
  writeln('AND result: ', result);
  
  result := (x < y) atau flag;
  writeln('OR result: ', result);
  
  result := tidak flag;
  writeln('NOT result: ', result);
  
  result := (x = y) atau (x <> y);
  writeln('Equality result: ', result);
selesai;

mulai
  { Arithmetic expressions }
  a := 10;
  b := 3;
  c := (a + b) * 2;
  d := a * b + c bagi 2;
  x := 15.75;
  y := 3.25;
  z := (x + y) * (x - y) / 2.0;
  
  { Mod and bagi operations }
  writeln('a mod b = ', a mod b);
  writeln('a bagi b = ', a bagi b);
  writeln('a bagi b = ', a / b);
  
  { Relational expressions }
  p := a > b;
  q := x <= y;
  r := a = b;
  s := x <> y;
  
  { Complex boolean expressions }
  p := (a > 0) dan (b < 10) atau tidak (x = y);
  q := tidak p dan (a + b > c);
  
  { Character expressions }
  ch1 := 'A';
  ch2 := 'B';
  r := ch1 = ch2;
  s := ch1 <> ch2;
  
  { Function calls in expressions }
  c := Calculate(a, b, '+') + Calculate(c, d, '*');
  writeln('Function result: ', c);
  
  { Mixed type expressions }
  x := a + b * 3.14;
  writeln('Mixed expression: ', x);
  
  { Test boolean operators }
  TestBooleanOps(a, b, benar);
  
  { Parentheses and precedence }
  c := (a + b) * (c - d) bagi (a mod b);
  p := (a > b) dan ((x < y) atau (ch1 = ch2));
  
  writeln('Final values - a:', a, ' b:', b, ' c:', c, ' d:', d);
  writeln('Final values - x:', x, ' y:', y, ' z:', z);
  writeln('Final values - p:', p, ' q:', q, ' r:', r, ' s:', s);
selesai.