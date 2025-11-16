program ArrayAndFunction;

var
  arr: array[1..5] of integer;
  i: integer;

function SumArray(a: array of integer; n: integer): integer;

var
  s, j: integer;

begin
  s := 0;
  for j := 0 to n - 1 do
    s := s + a[j];
  SumArray := s;
end;

begin
  for i := 1 to 5 do
    arr[i] := i * 2;
  writeln('Total sum: ', SumArray(arr, 5));
end.