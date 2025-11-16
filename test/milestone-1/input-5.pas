program BubbleSort;

var
  arr: array[1..5] of integer;
  i, j, temp: integer;

begin
  arr[1] := 5;
  arr[2] := 2;
  arr[3] := 8;
  arr[4] := 1;
  arr[5] := 3;

  for i := 1 to 4 do
  begin
    for j := 1 to 5 - i do
    begin
      if arr[j] > arr[j + 1] then
      begin
        temp := arr[j];
        arr[j] := arr[j + 1];
        arr[j + 1] := temp;
      end;
    end;
  end;

  writeln('Sorted array:');
  for i := 1 to 5 do
    writeln(arr[i]);
end.