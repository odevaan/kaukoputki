function st=dec2time(a,n);
%function st=dec2time(a,n);
%
%Converts a decimal number into time string
%using n significant digits.
%
%P. Paakkonen (2001)

if nargin<2 n=4; end;
a=a-24*floor(a/24);
sgn=sign(a);
a=abs(a);
h=fix(a);
mf=60*(a-h);
m=fix(mf);
s=60*(mf-m);
K=length(a);

for k=1:K
  switch n
    case 0, st(k,:)=sprintf('%4.0f',sgn(k).*a(k));
    case 1, st(k,:)=sprintf('%6.1f',sgn(k).*a(k));
    case 2, st(k,:)=sprintf('%4.0f:%02.0f',sgn(k).*h(k),mf(k)');
    case 3, st(k,:)=sprintf('%4.0f:%04.1f',sgn(k).*h(k),mf(k)');
    case 4, st(k,:)=sprintf('%4.0f:%02.0f:%02.0f',sgn(k).*h(k),m(k),s(k)');
    otherwise, eval(sprintf('st(k,:)=sprintf(''%%4.0f:%%02.0f:%%0%1.0f.%1.0ff'',[sgn(k).*h(k) m(k) s(k)]'');',n-1,n-4));
  end;
end;
