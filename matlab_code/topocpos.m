function [ra,de]=topocpos(ra,de,p,st0,long,lat,height);
%function [ra,de]=topocpos(ra,de,p,st0,long,lat,height);
%
%Calculates topocentric ra and de (rad) from geometric ones using
%using sidereal time at greenwich st0 (hours), geographical 
%longitude (westwards positive) and latitude (rad), and optional 
%height above the sea level (m).
%
%[Meeus, J., Astronomical algorithms, pp. 263-264, Willmann-Bell (1991)] 
%
%P. Paakkonen (2000)

if nargin<7 height=0; end;

H=st0*pi/12-long-ra;
u=atan(0.99664719*tan(lat));
rsinl=0.99664719*sin(u)+height.*sin(lat)/6378140;
rcosl=cos(u)+height.*cos(lat)/6378140;
den=cos(de)-rcosl.*sin(p).*cos(H);
dra=atan2(-rcosl.*sin(p).*sin(H),den);
de=atan2((sin(de)-rsinl.*sin(p)).*cos(dra),den);
ra=ra+dra;
ra=rem(ra,2*pi)+2*pi*(ra<0);
