function st=dec2dms(a,n);
%function st=dec2dms(a,n);
%
%Converts a decimal number into form of
%degree-minutes-seconds using n significant digits.
%
%P. Paakkonen (2000)


if nargin<2 n=4; end;
sgn=sign(a);
a=abs(a);
h=fix(a);
mf=60*(a-h);
m=fix(mf);
s=60*(mf-m);
K=length(a);

for k=1:K
  switch n
    case 0, st(k,:)=sprintf('%4.0f°',sgn(k).*a(k));
    case 1, st(k,:)=sprintf('%6.1f°',sgn(k).*a(k));
    case 2,
       if mf(k)>59.5 mf(k)=0; h(k)=h(k)+1; end;
       st(k,:)=sprintf('%4.0f°%02.0f''',sgn(k).*h(k),mf(k)');
    case 3, 
       if mf(k)>59.95 mf(k)=0; h(k)=h(k)+1; end;
       st(k,:)=sprintf('%4.0f°%04.1f''',sgn(k).*h(k),mf(k)');
    case 4, 
       if s(k)>59.5 s(k)=0; m(k)=m(k)+1; if m(k)>59 m(k)=0; h(k)=h(k)+1; end; end;
       st(k,:)=sprintf('%4.0f°%02.0f''%02.0f"',sgn(k).*h(k),m(k),s(k)');
    otherwise,
       if s(k)>60-0.5*10^(4-n) s(k)=0; m(k)=m(k)+1; if m(k)>59 m(k)=0; h(k)=h(k)+1; end; end;
       eval(sprintf('st(k,:)=sprintf(''%%4.0f°%%02.0f''''%%0%1.0f.%1.0ff"'',[sgn(k).*h(k) m(k) s(k)]'');',n-1,n-4));
  end;
end;
