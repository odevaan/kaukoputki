f=fopen('starnames.cat');
g=fopen('hichr.cat','r');
w=fopen('calistars.lst','w');
name=fgetl(f);
line=fgetl(g);
name=fgetl(f);
nro=0;
st={};
numb=0;
n=0;
while isstr(name)
  hr=str2double(name(6:9));
  while isstr(line) & hr>nro
    line=fgetl(g);
    nro=str2double(line(1:4));
    de=str2double(line(19:21));
    mag=str2double(line(46:51));
    if nro==hr & mag<3 & de>0 & de<70
       n=n+1;
       numb(n)=hr;
       st{n}=[name(16:22) ' - ' name(24:end)];
       fprintf(w,'%4.0f %s\n',hr,st{n});
    end;
 end;
 name=fgetl(f);
end;
fclose(f);
fclose(g);
fclose(w);