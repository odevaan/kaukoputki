function [ra0,de0]=astrometricpos(raa,dea,jde);
%function [ra,de]=astrometricpos(ra,de,jde);
%
%Calculates astrometric equatorial right ascension ra and
%declination de (rads) at given instant jde, effects
%nutation and annual aberration are reduced.
%
%[Meeus, Astronomical algorithms, chapter 22, Willmann-Bell (1991)]
%
%P.Paakkonen (2000,2003)

ra0=raa;
de0=dea;
for k=1:3;
   [ra,de]=apparentpos(ra0,de0,jde);
   ra0=raa+ra0-ra;
   de0=dea+de0-de;
   ra0=mod2pi(ra0);
end
