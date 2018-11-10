function [ha,de,A,h,R]=equ2atm(ha,de,lat,P,T);
%function [ha,de,A,h,R]=equ2atm(ha,de,lat,P,T);
%
%Calculates topocentric ra and de (rad) corrected for atmospheric
%refraction using sidereal time at greenwich st0 (hours), 
%geographical longitude (westwards positive) and latitude (rad), 
%and optional air pressure P (mbar) and temperature T (cels). 
%Also horizontal azimuth A and altitude h (rad), corrected for 
%refraction R, are calculated.
%
%[Meeus, J., Astronomical algorithms, pp. 101-103, Willmann-Bell (1991)] 
%
%P. Paakkonen (2000)

[A,h]=equ2horiz(ha,de,lat);
R=0.00029671./tan(h+0.179769./(57.29578*h+5.11));
if nargin>3
  R=R*P./1010.*283./(T+273);
end;
h=h+R;
h=h-(h<0).*R;
[ha,de]=horiz2equ(A,h,lat);
