function t=str2dec(st);
%function t=str2dec(st);
%
%Converts a vector of strings st of type 'hours:min:sec'
%or 'deg:min:sec' to decimal time or angle t.
%Delimeter can be any non-digit character except '.',
%instead of ':' like above.
%
%P.Paakkonen (2000)

[K,N]=size(st);
t=zeros(K,1); s=t;
if K>0 & N>0
   for k=1:K
      n=0; n=1; nn=1;
      [a,c,err,nn]=sscanf(st(n:end),'%[^0-9+-]',[1,2]);
      n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%d%[^0-9]',[1,2]); if ~isempty(a) t(k)=abs(a(1)); s(k)=1-2*(a(1)<0); end;
      n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%d%[^0-9]',[1,2]); if ~isempty(a) t(k)=t(k)+a(1)/60; end;
      n=n+nn-1; [a,c,err,nn]=sscanf(st(k,n:end),'%f%[^0-9]',[1,2]); if ~isempty(a) t(k)=t(k)+a(1)/3600; end;
   end;
   t=t.*s;
end;   
