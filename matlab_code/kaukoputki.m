%kaukoputki
%
%Jakokosken t�htikaukoputken ohjaus. Asettaa ohjausikkunan
%gui.m ja p�ivitt�� sit� sekunnin v�lein.
%
%Pertti P��kk�nen, syyskuu 2000.

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
