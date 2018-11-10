function [A,h]=equ2horiz(ha,de,lat);
%function [A,h]=equ2horiz(ha,de,lat);
%
%Converts equatorial our angle ha and declination de (rad) 
%into horizontal azimuth A and altitude h (rad) using
%the sidereal time in Greenwich st0 (hours) and geographical longitude
%and latitude (rad).
%
%P. Paakkonen (2000)

A=atan2(sin(ha),cos(ha).*sin(lat)-tan(de).*cos(lat));
h=asin(sin(lat).*sin(de)+cos(lat).*cos(de).*cos(ha));
A=mod2pi(A);
