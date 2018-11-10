function [ra,de,R,P,elong,phase,mag]=moon(jde,apparent);
%function [ra,de,R,P,elong,phase,mag]=moon(jde,apparent);
%
%Calculates geocentric equatorial right ascension ra,
%declination de (rads), distance R (km) and equatorial
%parallax P (rad) for given instant jde.
%
%[Meeus, Astronomical algorithms, p.307-313, Willmann-Bell (1991)]
%
%P.Paakkonen (2000)

[L,B,R]=moonecl(jde);
epsilon=ecliptic(jde);
if apparent
  [dphi,deps]=nutation(jde);
  epsilon=epsilon+deps;
  L=L+dphi;
end;
ra=atan2(sin(L).*cos(epsilon)-tan(B).*sin(epsilon),cos(L));
de=asin(sin(B).*cos(epsilon)+cos(B).*sin(epsilon).*sin(L));
P=asin(6378.14./R);
if nargout>4
   [L0,B0,R0]=heliocpos(jde,3);
   elong=acos(cos(B).*cos(L-L0+pi));
   phase=atan2(R0.*sin(elong),R/149.6e+6-R0.*cos(elong));
end;
nag=nan;
