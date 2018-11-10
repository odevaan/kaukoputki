function [ra,de,st,nro,pmra,pmde]=read(type,nro)

ra=0;
de=0;
st={'',''};
name='';
pmra=0;
pmde=0;
found=0;
switch type
case 2 % HR- kohde
   if ischar(nro)
      nro=upper(nro);
      f=fopen('starnames.cat','r');
      nfound=0;
      while ~feof(f) & ~nfound
         line=fgetl(f);
         const=line(20:22);
         name=upper([line(11:12) ' ' const ' ' line(13:15) ' ' const line(16:end)]);
         if ~isempty(findstr(nro,name))
            nfound=1;
            nro=str2double(line(6:9));
         end;
      end;
      if ~nfound 
         nro=-1; 
      end;
   end;
   if (nro>0 & nro<9111)
      f=fopen('hichr.cat','r');
      line=fgetl(f);
      st{1}=line(46:end);
      hr=-1;
      pos=(floor(nro*8978/9110))*(1+length(line));
      if pos<0 pos=0; end;
      fst=fseek(f,pos,0);
      while isstr(line) & ~found & hr<nro
         line=fgetl(f);
         hr=str2double(line(1:4));
         found=(hr==nro);
         if hr>nro
            pos=-10*(1+length(line));
            if fseek(f,pos,0)<0 fseek(f,0,-1); end;
            hr=0;
         end;
         
      end;
      if found 
         ra=str2dec(line(6:17))*pi/12;
         de=str2dec(line(19:30))*pi/180;
         pmra=str2dec(line(32:37))*pi/648000;
         pmde=str2dec(line(39:44))*pi/648000;
         st{2}=line(46:end);
         namenro=str2double(line(94:97));
         if ~isnan(namenro)
            g=fopen('starnames.cat','r');
            fpos=floor(namenro/3482*81171)-500;
            if fpos<0 fpos=0; end;
            fseek(g,fpos,0);
            fgetl(g);
            nfound=0;
            while ~feof(g) & ~nfound
               line=fgetl(g);
               n=str2double(line(1:4));
               nfound=(n==namenro);
               if n>namenro
                  if fseek(g,-500,0)<0 fseek(g,0,-1); end;
               end;
            end;
            if nfound 
               const=line(20:22);
               st{2}=st{2}(1:48);
               if line(12)~=' ' st{2}=[st{2} ' ' line(11:12) ' ' const]; end;
               if line(15)~=' ' st{2}=[st{2} ' ' line(13:15) ' ' const]; end;
               if line(16)~=' ' st{2}=[st{2} ' ' line(16:end)]; end;
            end;
         end;
      else
         nro=-1;
      end;
      fclose(f);
   else
      nro=-1;
   end;
case 3 % NGC kohde
   if (nro>0 & nro<7841)
      f=fopen('ngc2000.cat','r');
      line=fgetl(f);
      st{1}=line(24:end);
      ngc=-1;
      pos=(nro-1)*(1+length(line));
      fst=fseek(f,pos,0);
      while isstr(line) & ~found & ngc<nro
         line=fgetl(f);
         ngc=str2double(line(1:4));
         found=(ngc==nro);
      end;
      if found 
         ra=str2dec(line(5:12))*pi/12;
         de=str2dec(line(14:22))*pi/180;
         st{2}=line(24:end); 
      else
         nro=-1;
      end;
      fclose(f);
   end;
case 4 % IC kohde
   if (nro>0 & nro<5387)
      f=fopen('ic2000.cat','r');
      line=fgetl(f);
      st{1}=line(24:end);
      ic=-1;
      pos=(nro-1)*(1+length(line));
      fst=fseek(f,pos,0);
      while isstr(line) & ~found & ic<nro
         line=fgetl(f);
         ic=str2double(line(1:4));
         found=(ic==nro);
      end;
      if found 
         ra=str2dec(line(5:12))*pi/12;
         de=str2dec(line(14:22))*pi/180;
         st{2}=line(24:end); 
      else
         nro=-1;
      end;
      fclose(f);
   end;
case 5
   if (nro>0 & nro<111)
      f=fopen('messier.cat','r');
      line=fgetl(f);
      st{1}=line(24:end);
      m=-1;
      pos=(nro-1)*(1+length(line));
      fst=fseek(f,pos,0);
      while isstr(line) & ~found & m<nro
         line=fgetl(f);
         m=str2double(line(1:3));
         found=(m==nro);
      end;
      if found 
         ra=str2dec(line(5:12))*pi/12;
         de=str2dec(line(14:22))*pi/180;
         st{2}=line(24:end); 
      else
         nro=-1;
      end;
      fclose(f);
   end;
   
   
   
end;
