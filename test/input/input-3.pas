program EvenOdd;

variabel
  i: integer;

mulai
  i := 0;
  selama i < 5 do
  mulai
    if i mod 2 = 0 maka
      writeln(i, ' is even')
    selain-itu
      writeln(i, ' is odd');
    i := i + 1;
  selesai;
selesai.