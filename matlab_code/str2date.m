function [y,m,d,ut]=str2date(st);
%function [y,m,d]=str2date(st);
%function [y,m,d,ut]=str2date(st);
%
%Converts a vector of string st of type 'year.month.day hours:min:sec'
%to years y, months m, days d and optional universal time ut.
%Delimeter can be any non-digit character, except '.', '+' and '-'.
%
%P.Paakkonen (2000)

[K,N]=size(st);
t=zeros(K,1);
if K>0 & N>0
   for k=1:K
      n=0; n=1; nn=1;
      [a,c,err,nn]=sscanf(st(n:end),'%[^0-9+-]',[1,2]);
      n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%d%[^0-9]',[1,2]); if ~isempty(a) y=a(1); end;
      n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%d%[^0-9]',[1,2]); if ~isempty(a) m=a(1); end;
      n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%d%[^0-9]',[1,2]); if ~isempty(a) d=a(1); end;
      if any(a=='.')
         n=n+nn-1; [a,c,err,nn]=sscanf(['.' st(k,n:end)],'%f%[^0-9]',[1,2]); if ~isempty(a) d=d+a(1); end;
      else
         n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%d%[^0-9]',[1,2]); if ~isempty(a) a, d=d+a(1)/24; end;
         n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%d%[^0-9]',[1,2]); if ~isempty(a) d=d+a(1)/1440; end;
         n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%f%[^0-9]',[1,2]); if ~isempty(a) d=d+a(1)/86400; end;
      end;
   end;
end;
if nargout>3
  dt=d;
  d=fix(d);
  ut=24*(dt-d);
end;

