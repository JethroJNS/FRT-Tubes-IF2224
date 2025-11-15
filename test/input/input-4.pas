program ArrayAndFunction;

variabel
  arr: larik[1..5] dari integer;
  i: integer;

fungsi SumArray(a: larik dari integer; n: integer): integer;

variabel
  s, j: integer;

mulai
  s := 0;
  untuk j := 0 ke n - 1 lakukan
    s := s + a[j];
  SumArray := s;
selesai;

mulai
  untuk i := 1 ke 5 lakukan
    arr[i] := i * 2;
  writeln('Total sum: ', SumArray(arr, 5));
selesai.