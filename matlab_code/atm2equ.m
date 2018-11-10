function [ha0,de0,A,h,R]=atm2equ(haa,dea,varargin);
%function [ha,de,A,h,R]=atm2equ(ha,de,lat,P,T);
%
%Calculates topocentric ha and de (rad) corrected for atmospheric
%refraction using geographical latitude (rad), 
%and optional air pressure P (mbar) and temperature T (cels). 
%Also horizontal azimuth A and altitude h (rad), corrected for 
%refraction R, are calculated.
%
%[Meeus, J., Astronomical algorithms, pp. 101-103, Willmann-Bell (1991)] 
%
%P. Paakkonen (2000)

ha0=haa;
de0=dea;
for k=1:6;
   [ha,de,A,h,R]=equ2atm(ha0,de0,varargin{:});
   ha0=haa+ha0-ha;
   de0=dea+de0-de;
   ha0=mod2pi(ha0);
end;
