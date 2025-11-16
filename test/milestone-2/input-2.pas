program Input2;
variabel
  i, j: integer;
  flag: boolean;
mulai
  flag := benar;
  
  jika flag maka
    writeln('Kondisi benar');
  
  untuk i := 1 ke 10 lakukan
    writeln(i);
  
  j := 10;
  selama j > 0 lakukan
    mulai
      writeln(j);
      j := j - 1;
    selesai;
    
  ulangi
    i := i + 1;
  sampai i > 5;
selesai.