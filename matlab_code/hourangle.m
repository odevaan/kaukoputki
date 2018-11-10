function H=hourangle(ra,st0,long);
%function H=hourangle(ra,st0,long);
%
%Calculates the local hour angle H (rad) from
%right ascension ra (rad), sidereal time at
%Greenwich st0 (hours) and longitude (rad).

H=st0*pi/12-ra-long;
H=mod2pi(H);
