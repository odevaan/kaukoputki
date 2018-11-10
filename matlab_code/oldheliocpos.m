function [L,B,R]=oldheliocpos(jde,p);
%function [L,B,R]=oldheliocpos(jde,p);
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
%For 0<e<1 for elliptical orbit and e=1 parabolic orbit.
%
%[Meeus, J., Astronomical algorithms, chapters 31-33, Willmann-Bell (1991)]
%
%P. Paakkonen (2000)

global vsopvar vsopind;
S=prod(size(p));
N=length(jde(:));
t=ones(6,1)*(jde(:)'-2451545)/365250; t(1,:)=1;
t=cumprod(t);
pi2=2*pi;

L=zeros(1,N); B=L; R=L;

if S==1
  if (p>0 & p<10)
    for v_t=0:5
      I=squeeze(vsopind(p,1,v_t+1,:));
      if I(2)>0
         V=vsopvar(I(1)+(0:I(2)-1),:);
        eval(sprintf('L=L+sum(V(:,1)*ones(1,N).*cos(V(:,2)*ones(1,N)+V(:,3)*t(2,:)),1).*t(%1.0f,:);',v_t+1));
      end;
      L=mod2pi(L);
     end;
    for v_t=0:5
      I=squeeze(vsopind(p,2,v_t+1,:));
      if I(2)>0
        V=vsopvar(I(1)+(0:I(2)-1),:);
        eval(sprintf('B=B+sum(V(:,1)*ones(1,N).*cos(V(:,2)*ones(1,N)+V(:,3)*t(2,:)),1).*t(%1.0f,:);',v_t+1));
      end;
    end;
    for v_t=0:5
      I=squeeze(vsopind(p,3,v_t+1,:));
      if I(2)>0
        V=vsopvar(I(1)+(0:I(2)-1),:);
        eval(sprintf('R=R+sum(V(:,1)*ones(1,N).*cos(V(:,2)*ones(1,N)+V(:,3)*t(2,:)),1).*t(%1.0f,:);',v_t+1));
      end;
    end;
  end;
elseif S==6
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