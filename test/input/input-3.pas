program ComplexTypes;
tipe
  Point = rekaman
    x, y: integer;
  selesai;
  Matrix = larik[1..3, 1..3] dari real;
variabel
  p: Point;
  m: Matrix;
mulai
  p.x := 10;
  p.y := 20;
  m[1,1] := 1.5;
selesai.