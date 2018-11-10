function [ra,de]=precess(ra0,de0,jd0,jd);
%function [ra,de]=precess(ra0,de0,jd0,jd);
%
%Calculates equatorial right ascension ra and declination de (rads)
%for the epoch and mean equinox of jd, reduced from ra0 and de0 (rads)
%for the epoch and mean equinox of jd0.
%
%[Meeus, Astronomical algorithms, chapter 20, Willmann-Bell (1991)]
%
%P.Paakkonen (2000)

T=(jd0-2451545)/36525;
t=(jd-jd0)/36525;

T2=T.*T;
t2=t.*t;
t3=t2.*t;

temp=(2306.2181+1.39656*T-0.000139*T2).*t;
zeta=(temp+(0.30188-0.000344*T).*t2+0.017998*t3)/206264.806247;
   z=(temp+(1.09468+0.000066*T).*t2+0.018203*t3)/206264.806247;
theta=((2004.3109-0.8533*T-0.000217*T2).*t-(0.42665+0.000217*T).*t2-0.041833*t3)/206264.806247;
ra0=ra0+zeta;
A=cos(de0).*sin(ra0);
B=cos(theta).*cos(de0).*cos(ra0)-sin(theta).*sin(de0);
C=sin(theta).*cos(de0).*cos(ra0)+cos(theta).*sin(de0);
ra=atan2(A,B)+z;
de=asin(C);
ind=find(abs(cos(de0))<0.01);
if ~isempty(ind) 
  de(ind)=acos(sqrt(A(ind).*A(ind)+B(ind).*B(ind))); 
end;
ra=rem(ra,2*pi)+2*pi*(ra<0);
