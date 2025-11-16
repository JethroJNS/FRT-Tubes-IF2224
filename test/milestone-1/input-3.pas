program EvenOdd;

var
  i: integer;

begin
  i := 0;
  while i < 5 do
  begin
    if i mod 2 = 0 then
      writeln(i, ' is even')
    else
      writeln(i, ' is odd');
    i := i + 1;
  end;
end.