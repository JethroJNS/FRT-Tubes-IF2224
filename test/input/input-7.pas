program BasicStructureTest;

konstanta
  MAX_SIZE = 100;
  PI = 3.14159;
  APP_NAME = 'Basic Test';
  INITIAL = 'X';

tipe
  ScoreRange = 0..100;
  NameArray = larik[1..50] dari string;
  Coord = larik[1..3] dari real;

variabel
  id, count, total: integer;
  price, discount, finalPrice: real;
  isActive, isValid: boolean;
  grade: char;
  scores: ScoreRange;
  names: NameArray;
  point: Coord;

prosedur InitializeData;
mulai
  id := 1;
  count := 0;
  total := 100;
  price := 99.99;
  discount := 0.1;
  isActive := benar;
  isValid := salah;
  grade := 'A';
selesai;

mulai
  InitializeData;
  finalPrice := price * (1 - discount);
  
  jika isActive dan isValid maka
    writeln('System aktif dan valid')
  selainitu
    writeln('System tidak aktif atau tidak valid');

  untuk count := 1 ke 5 lakukan
    writeln('Count: ', count);

  writeln('Program: ', APP_NAME);
  writeln('Final Price: ', finalPrice);
selesai.