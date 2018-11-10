function [L,B,R]=heliocpos(jde,p);
%function [L,B,R]=heliocpos(jde,p);
%
%Calculates heliocentric position of planet p
%for given instants jde, i.e, heliocentric 
%longitude L, latitude B and radius vector R,
%for mean equator and equinox of date, except
%for Pluto, which is for standard epoch J2000.0
%
%p can also be a vector of orbital elements:
%p(1) = julian date of the perihelion
%p(2) = eccentricity of the orbit (e)
%p(3) = perihelion distance (a(1-e))
%p(4) = inclination on the plane of the ecliptic (i)
%p(5) = argument of the perihelion (omega)
%p(6) = longitude of the ascending node (Omega)
%p(7),p(8)  = g,k parameters for magnitudes (optional)
%p(9),p(10) = H,G parameters for magnitudes (optional)
%For 0<e<1 for elliptical orbit and e=1 parabolic orbit.
%
%[Meeus, J., Astronomical algorithms, chapters 31-33, Willmann-Bell (1991)]
%
%P. Paakkonen (2000)

S=prod(size(p));
N=length(jde(:));
pi2=2*pi;

if S==1
   switch p
      case 1, [L,B,R]=mercury(jde);
      case 2, [L,B,R]=venus(jde);
      case 3, [L,B,R]=earth(jde);
      case 5, [L,B,R]=jupiter(jde);
      case 4, [L,B,R]=mars(jde);
      case 6, [L,B,R]=saturn(jde);
      case 7, [L,B,R]=uranus(jde);
      case 8, [L,B,R]=neptune(jde);
      case 9, [L,B,R]=pluto(jde);
      otherwise error('Unknown planet');
   end;
elseif S>=6
  if p(2)>=0 & p(2)<1
    a=p(3)/(1-p(2));
    if a M=(jde(:)'-p(1))*0.01720209895/a^1.5; else M=zeros(size(jde(:)')); end;
    E=M; Ep=E+1;
    while all(abs(E-Ep)>1e-10)
      Ep=E;
      den=1-p(2)*cos(E);
      E=E+(M+p(2)*sin(E)-E)./den;
    end;
    v=2*atan(sqrt((1+p(2))/(1-p(2)))*tan(E/2));
    R=a*den;
    u=v+p(5);
    L=atan2(cos(p(4))*sin(u),cos(u))+p(6);
    B=asin(sin(u)*sin(p(4)));
  elseif p(2)==1
    W=0.018245581225*(jde(:)'-p(1))/(p(3)*sqrt(p(3)));
    Y=(W+sqrt(W.*W+1)).^(1/3);
    s=Y-1./Y;
    v=2*atan(s);
    R=p(3)*(1+s.*s);
    u=v+p(5);
    L=atan2(cos(p(4))*sin(u),cos(u))+p(6);
    B=asin(sin(u)*sin(p(4)));
  else
    error('No other than circular, elliptical or parabolic motion supported.');
  end;
else
  error('Weird orbital elements.');
end;