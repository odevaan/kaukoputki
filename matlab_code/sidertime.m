function st0=sidertime(jd,dphi,epsilon);
%function st0=sidertime(jd);
%function st0=sidertime(jd,dphi,epsilon);
%
%Calculates the sidereal time at Greenwich for julian day jd.
%If the nutation in longitude (dphi) and the true obliquity
%of the ecliptic are given then the apparent sidereal time
%is calculated.
%
%[Meeus, J., Astronomical algorithms, pp. 83-84, Willmann-Bell (1991)]
%
%P. Paakkonen (2000)

T=(jd-2451545)/36525;
st0=4.894961212736+6.30038809898496*(jd-2451545)+T.*T.*(6.7707081e-006-T*4.50873e-010);
if nargin>2
  st0=st0+dphi.*cos(epsilon);
end;
st0=rem(st0*12/pi,24)+(st0<0)*24;
