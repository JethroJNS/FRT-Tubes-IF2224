program BubbleSort;

variabel
  arr: array[1..5] dari integer;
  i, j, temp: integer;

mulai
  arr[1] := 5;
  arr[2] := 2;
  arr[3] := 8;
  arr[4] := 1;
  arr[5] := 3;

  untuk i := 1 ke 4 lakukan
  mulai
    untuk j := 1 ke 5 - i lakukan
    mulai
      if arr[j] > arr[j + 1] then
      mulai
        temp := arr[j];
        arr[j] := arr[j + 1];
        arr[j + 1] := temp;
      selesai;
    selesai;
  selesai;

  writeln('Sorted array:');
  untuk i := 1 ke 5 lakukan
    writeln(arr[i]);
selesai.