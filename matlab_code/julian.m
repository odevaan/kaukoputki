function jd=julian(y,m,d,ut);
%function jd=julian(y,m,d);
%function jd=julian(y,m,d,ut);
%
%Calculates julian date of year y, month m, day d
%and universal time ut. d can be decimal number(s) 
%of universal time and ut is optional. 
%Any of these can be either scalars or vectors of proper sizes.
%
%[Meeus, Astronomical algorithms, p.59-66, Willmann-Bell (1991)]
%
%P.Paakkonen (2000)

if nargin>3 d=fix(d)+ut/24; end;

X=fix((m+9.5)/12);
Y=y-1+X;
M=m+12*(1-X);
A=fix(Y/100);
B=2-A+fix(A/4);
jd=fix(365.25*(Y+4716))+fix((M+1)*30.6001)+d+B-1524.5;
jd=jd-(jd<2299161).*B;