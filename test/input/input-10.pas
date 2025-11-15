program SubprogramTest;

variabel
  globalCounter: integer;

fungsi Factorial(n: integer): integer;
variabel
  result, i: integer;
mulai
  result := 1;
  untuk i := 1 ke n lakukan
    result := result * i;
  Factorial := result;
selesai;

fungsi IsPrime(num: integer): boolean;
variabel
  i: integer;
  prime: boolean;
mulai
  prime := benar;
  jika num < 2 maka
    prime := salah
  selainitu
    untuk i := 2 ke num bagi 2 lakukan
      jika num mod i = 0 maka
        prime := salah;
  IsPrime := prime;
selesai;

fungsi MaxOfThree(a, b, c: integer): integer;
mulai
  jika a >= b dan a >= c maka
    MaxOfThree := a
  selainitu jika b >= c maka
    MaxOfThree := b
  selainitu
    MaxOfThree := c;
selesai;

prosedur Swap(var x, y: integer);
variabel
  temp: integer;
mulai
  temp := x;
  x := y;
  y := temp;
selesai;

prosedur IncrementCounter;
mulai
  globalCounter := globalCounter + 1;
selesai;

prosedur PrintArray(arr: larik[1..5] dari integer; size: integer);
variabel
  i: integer;
mulai
  write('Array: [');
  untuk i := 1 ke size lakukan
  mulai
    write(arr[i]);
    jika i < size maka
      write(', ');
  selesai;
  writeln(']');
selesai;

prosedur ProcessData(value: integer; var result: integer; flag: boolean);
mulai
  jika flag maka
    result := value * 2
  selainitu
    result := value bagi 2;
selesai;

mulai
  variabel
    num1, num2, num3, output: integer;
    arr: larik[1..5] dari integer;
    i: integer;

  globalCounter := 0;
  num1 := 5;
  num2 := 12;
  num3 := 8;

  { Function calls }
  writeln('Factorial of 5: ', Factorial(5));
  writeln('Is 17 prime? ', IsPrime(17));
  writeln('Max of 5, 12, 8: ', MaxOfThree(num1, num2, num3));

  { Procedure calls with var parameters }
  writeln('Before swap: num1=', num1, ' num2=', num2);
  Swap(num1, num2);
  writeln('After swap: num1=', num1, ' num2=', num2);

  { Global variable modification }
  untuk i := 1 ke 3 lakukan
    IncrementCounter;
  writeln('Global counter: ', globalCounter);

  { Array processing }
  untuk i := 1 ke 5 lakukan
    arr[i] := i * 10;
  PrintArray(arr, 5);

  { Procedure with multiple parameters }
  ProcessData(20, output, benar);
  writeln('ProcessData result with flag true: ', output);
  
  ProcessData(20, output, salah);
  writeln('ProcessData result with flag false: ', output);

  { Nested function calls }
  output := Factorial(MaxOfThree(3, 1, 4));
  writeln('Factorial of max(3,1,4): ', output);

  { Complex expressions with function calls }
  output := Factorial(3) + Factorial(4) - MaxOfThree(10, 20, 15);
  writeln('Complex expression result: ', output);
selesai.