function [p,epoch,name]=readedb(name);
%
%p(7:8):  g,k parameters
%p(9:10): H,G parameters

found=[];
p=[];
flist=dir('*.edb');
for j=1:length(flist);
   f=fopen(flist(j).name,'r');
   line=' ';
  while isstr(line) & isempty(found)
     line=fgetl(f);
     ind=findstr(line,',');
     if ~isempty(ind) & line(1)~='#'
        found=findstr(upper(line(1:ind(1))),upper(name));
        if ~isempty(found) & line(ind(1)+1)=='e' & length(ind)>=12
           name=line(1:ind(1)-1);
           p=zeros(6,1);
           %disp(line);
           p(4)=str2double(line(ind(2)+1:ind(3)-1))*pi/180;
           p(6)=str2double(line(ind(3)+1:ind(4)-1))*pi/180;
           p(5)=str2double(line(ind(4)+1:ind(5)-1))*pi/180;
              a=str2double(line(ind(5)+1:ind(6)-1));
              n=str2double(line(ind(6)+1:ind(7)-1));
           p(2)=str2double(line(ind(7)+1:ind(8)-1));
           p(3)=a*(1-p(2));
              M=str2double(line(ind(8)+1:ind(9)-1))*pi/180;
                 E=edbdate(line(ind(9)+1:ind(10)-1));
             epoch=edbdate(line(ind(10)+1:ind(11)-1));
           if n==0 | isempty(n) | isnan(n)
              n=0.01720209895/sqrt(a^3);
           end
           p(1)=E-M/n;
           if line(ind(11)+1)=='g'
              ind(11)=ind(11)+1;
              p(7)=str2double(line(ind(11)+1:ind(12)-1));
              p(8)=str2double(line(ind(12)+1:end));
           else
              if line(ind(11)+1)=='H' ind(11)=ind(11)+1; end;
              p(9)=str2double(line(ind(11)+1:ind(12)-1));
              p(10)=str2double(line(ind(12)+1:end));
           end;   
        end;
     end
  end;
  fclose(f);
end;

      

  
  