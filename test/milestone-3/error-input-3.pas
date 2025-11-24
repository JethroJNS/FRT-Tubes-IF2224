program ArrayBounds;
variabel
  arr: larik[1..10] dari integer;
  bigArr: larik[1..1000] dari integer;
  invalidArr: larik[10..1] dari integer;  { SEMANTIC ERROR: Lower bound > upper bound }
mulai
  arr[1] := 100;    { Valid }
  arr[10] := 200;   { Valid }
  arr[0] := 300;    { SEMANTIC ERROR: Index out of bounds }
  arr[11] := 400;   { SEMANTIC ERROR: Index out of bounds }
selesai.