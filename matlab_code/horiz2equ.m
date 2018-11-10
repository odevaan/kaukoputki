function [ha,de]=horiz2equ(A,h,lat);
%function [ha,de]=horiz2equ(A,h,lat);
%
%Converts horizontal azimuth A and altitude h (rad) 
%into equatorial hour angle ha and declination de (rad) using
%the sidereal time in Greenwich st0 (hours) and geographical longitude
%and latitude (rad).
%
%P. Paakkonen (2000)


ha=atan2(sin(A),cos(A).*sin(lat)+tan(h).*cos(lat));
de=asin(sin(lat).*sin(h)-cos(lat).*cos(h).*cos(A));
ha=mod2pi(ha);
