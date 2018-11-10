function [ra,de]=apparentpos(ra,de,jde);
%function [ra,de]=apparentpos(ra,de,jde);
%
%Calculates apparent equatorial right ascension ra and
%declination de (rads) at given instant jde, corrected
%for nutation and annual aberration.
%
%[Meeus, Astronomical algorithms, chapter 22, Willmann-Bell (1991)]
%
%P.Paakkonen (2000)

[dphi,deps]=nutation(jde);
epsilon=ecliptic(jde);
dra1=(cos(epsilon)+sin(epsilon).*sin(ra).*tan(de)).*dphi-cos(ra).*tan(de).*deps;
dde1=(sin(epsilon).*cos(ra)).*dphi+sin(ra).*deps;

T=(jde(:)'-2451545)/36525;
T2=T.*T;
T3=T2.*T;
e=0.016708617-0.000042037*T-0.0000001236*T2;
p=1.79659568+0.03001146*T+0.000008029*T2;
M=rem(6.2400599667+628.301955326*T-0.0000027200*T2-0.00000000838*T3,2*pi);
L0=rem(4.895062994+628.331966786*T+0.0000052918*T2,2*pi);
C=(0.033416074-0.0000840725*T-0.000000244*T2).*sin(M);
C=C+(0.0003489437-0.0000017628*T).*sin(2*M);
C=C+0.000005061*sin(3*M);
L=L0+C;
R=1.000001018*(1-e.^2)./(1+e.*cos(M+C));
k=0.00009936508497;
temp=cos(epsilon).*(tan(epsilon).*cos(de)-sin(ra).*sin(de));
dra2=-k*(cos(ra).*cos(L).*cos(epsilon)+sin(ra).*sin(L))./cos(de);
dra2=dra2+k*e.*(cos(ra).*cos(p)+sin(ra).*sin(p))./cos(de);
dde2=-k*(cos(L).*temp+cos(ra).*sin(de).*sin(L));
dde2=dde2+k*e.*(cos(p).*temp+cos(ra).*sin(de).*sin(p));
ra=ra+dra1+dra2;
de=de+dde1+dde2;
ra=rem(ra,2*pi)+2*pi*(ra<0);
