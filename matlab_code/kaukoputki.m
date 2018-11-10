%kaukoputki
%
%Jakokosken tähtikaukoputken ohjaus. Asettaa ohjausikkunan
%gui.m ja päivittää sitä sekunnin välein.
%
%Pertti Pääkkönen, syyskuu 2000.

h0=gui;
t1=clock;
t2=0*t1;

while ~isempty(findobj('Tag','Jakokoski'))
  update;
  while fix(t1(6))==fix(t2(6)) 
     t2=clock;
     pause(0);
  end;
  t1=t2;
end;
