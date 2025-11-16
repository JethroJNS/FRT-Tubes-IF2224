program Input8;

variabel
  i, j, k: integer;
  x, y: real;
  condition1, condition2, result: boolean;

fungsi CheckConditions(a, b: integer; flag: boolean): boolean;
mulai
  jika a > b dan flag maka
    CheckConditions := benar
  selainitu
    CheckConditions := salah;
selesai;

prosedur ProcessLoop(limit: integer);
variabel
  counter: integer;
mulai
  counter := 1;
  selama counter <= limit lakukan
  mulai
    jika counter mod 2 = 0 maka
      writeln(counter, ' adalah genap')
    selainitu
      writeln(counter, ' adalah ganjil');
    
    counter := counter + 1;
  selesai;
selesai;

prosedur NestedIfDemo(num: integer);
mulai
  jika num > 0 maka
  mulai
    writeln('Positif');
    jika num > 100 maka
      writeln('Lebih dari 100')
    selainitu
      writeln('Kurang dari atau sama dengan 100');
  selesai
  selainitu jika num < 0 maka
    writeln('Negatif')
  selainitu
    writeln('Nol');
selesai;

mulai
  i := 15;
  j := 25;
  x := 7.5;
  y := 12.3;
  condition1 := benar;
  condition2 := salah;

  { If-else statements }
  NestedIfDemo(i);
  NestedIfDemo(-5);
  NestedIfDemo(0);

  { While loop }
  ProcessLoop(6);

  { For loops }
  untuk k := 1 ke 8 lakukan
  mulai
    writeln('For loop iteration: ', k);
  selesai;

  untuk k := 10 turunke 1 lakukan
  mulai
    writeln('Countdown: ', k);
  selesai;

  { Complex conditions }
  result := CheckConditions(i, j, condition1);
  writeln('Check result: ', result);

  result := (x > y) atau (i < j) dan tidak condition2;
  writeln('Complex condition: ', result);
selesai.