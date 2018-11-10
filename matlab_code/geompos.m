function [ra,de,delta,p,elong,phase,mag]=geompos(jde,planet,apparent);
%function [ra,de,delta,p,elong,phase,mag]=geompos(jde,planet,apparent);
%
%Calculates geometric position of planet for
%given instant(s) jde, i.e., right ascension re, 
%declination de for mean equator and equinox
%of date, geometric distance delta,parallax p,
%elongation and phase angle.
%If apparent is nonzero, then ra and de are corrected 
%for aberration and nutation.
%
%[Meeus, J., Astronomical algorithms, 
%chapter 32, Willmann-Bell (1991)]
%
%P. Paakkonen (2000)

M=prod(size(planet));
T=(jde(:)'-2451545)/36525;
T2=T.*T;
T3=T2.*T;
N=length(T);
[dphi,deps]=nutation(jde);
epsilon=ecliptic(jde);
[L0,B0,R0]=heliocpos(jde,3);

if (M==1 & planet==9) | length(planet)>=6
  %for Pluto we have orbit for mean epoch and equinox of J2000.0
  %precession parameters for precession between date and J2000.0
  zeta=(2306.2181*T+0.30188*T2+0.017998*T3)/206264.806247;
     z=(2306.2181*T+1.09468*T2+0.018203*T3)/206264.806247;
  theta=(2004.3109*T-0.42665*T2-0.041833*T3)/206264.806247;
  xx=cos(zeta).*cos(z).*cos(theta)-sin(zeta).*sin(z);
  xy=sin(zeta).*cos(z)+cos(zeta).*sin(z).*cos(theta);
  xz=cos(zeta).*sin(theta);
  yx=-cos(zeta).*sin(z)-sin(zeta).*cos(z).*cos(theta);
  yy=cos(zeta).*cos(z)-sin(zeta).*sin(z).*cos(theta);
  yz=-sin(zeta).*sin(theta);
  zx=-cos(z).*sin(theta);
  zy=-sin(z).*sin(theta);
  zz=cos(theta);
  
    %PM=[xx xy xz; yx yy yz; zx zy zz];
    %here we have coordinates of Sun for mean ecliptic and equinox of date 
    x0=R0.*cos(B0).*cos(L0);
    y0=R0.*(cos(B0).*sin(L0).*cos(epsilon)-sin(B0).*sin(epsilon));
    z0=R0.*(cos(B0).*sin(L0).*sin(epsilon)+sin(B0).*cos(epsilon));
    %pt=PM*[x0; y0; z0];
    x1=xx.*x0+xy.*y0+xz.*z0;
    y1=yx.*x0+yy.*y0+yz.*z0;
    z1=zx.*x0+zy.*y0+zz.*z0;
    
    %and now we have ecliptical rectangular coordinates of Sun for J2000
    EM=[1 -0.000000479966 0; 0.000000440360 0.917482137087 0.397776982902; -0.000000190919 -0.397776982902 0.917482137087];
    p0=EM*[x1; y1; z1];
    %and finally, we have heliocentric rectangular coordinates of Sun for J2000
    x0=p0(1,:);
    y0=p0(2,:);
    z0=p0(3,:);
else
  %For all others mean epoch and equinox of date.
  x0=R0.*cos(B0).*cos(L0);
  y0=R0.*cos(B0).*sin(L0);
  z0=R0.*sin(B0);
end;

epsilon=epsilon+deps;
tau=0; taup=1; n=0;
if (M==1 & planet~=3 & planet>0 & planet<10) | M>1
  while max(abs(tau-taup))>1.2e-5 & n<6
    [L,B,R]=heliocpos(jde-tau,planet);
    x=R.*cos(B).*cos(L)-x0;
    y=R.*cos(B).*sin(L)-y0;
    z=R.*sin(B)-z0;
    delta=sqrt(x.*x+y.*y+z.*z);
    taup=tau;
    tau=0.0057755183*delta;
    n=n+1;
  end;
  lambda=atan2(y,x);
  beta=atan2(z,sqrt(x.^2+y.^2));
  
  if (M==1 & planet==9) | length(planet)>=6
    %Pluto was calculated in J2000.0 frame. 
    eta=(47.0029*T-0.03302*T2+0.000060*T3)/206264.806247;
    pii=174.876384*pi/180-(869.8089*T-0.03536*T2)/206264.806247;
    pee=(5029.0966*T+1.11113*T2-0.000006*T3)/206264.806247;
    lambda0=lambda;
    beta0=beta;
    lambda=pee+pii-atan2(cos(eta).*cos(beta0).*sin(pii-lambda0)-sin(eta).*sin(beta0),cos(beta0).*cos(pii-lambda0));
    beta=asin(cos(eta).*sin(beta0)+sin(eta).*cos(beta0).*sin(pii-lambda0));
    %now we are back in mean equator and equinox of date
  end; 
  if apparent
    e=0.016708617-0.000042037*T-0.0000001236*T2;
    p=1.79659568+0.03001146*T+0.000008029*T2;
    LS=L0+pi;
    BS=-B0;
    lambda=lambda-0.00009936508497*(cos(LS-lambda)-e.*cos(p-lambda))./cos(beta)+dphi;
    beta=beta-0.00009936508497*sin(beta).*(sin(LS-lambda)-e.*sin(p-lambda));
  end;
  L=lambda-0.024382*T-0.00000541*T2;
  deltaL=-0.43793e-6+0.18985e-6*(cos(L)+sin(L)).*tan(beta);
  deltaB=0.18985e-6*(cos(L)-sin(L));
  lambda=lambda+deltaL;
  beta=beta+deltaB;
  ra=atan2(sin(lambda).*cos(epsilon)-tan(beta).*sin(epsilon),cos(lambda));
  de=asin(sin(beta).*cos(epsilon)+cos(beta).*sin(epsilon).*sin(lambda));
elseif M==1 & planet==0
  [L,B,R]=heliocpos(jde,3);
  delta=R; 
  lambda=L+pi;
  beta=-B;
  L=lambda-0.024382*T-0.00000541*T2;
  deltaL=-0.43793e-6;
  deltaB=0.18985e-6*(cos(L)-sin(L));
  lambda=lambda+deltaL;
  beta=beta+deltaB;
  if apparent
    lambda=lambda+dphi-0.005775518*delta.*aberration(jde);
  end;
  ra=atan2(sin(lambda).*cos(epsilon)-tan(beta).*sin(epsilon),cos(lambda));
  de=asin(sin(beta).*cos(epsilon)+cos(beta).*sin(epsilon).*sin(lambda));
end;
p=4.2635e-5./delta;
ra=mod2pi(ra);
elong=acos(cos(B).*cos(L-L0+pi));
phase=nan;
if M==1 & planet>0 
   phase=atan2(R0.*sin(elong),R-R0.*cos(elong));
end;
      
mag=nan;
if length(planet)>8
   % H,G model
   H=planet(9);
   G=planet(10);
   %beta=acos((R.^2+delta.^2-R0.^2)/(2*R.*delta));
   psi_1=exp(-3.33*tan(beta/2).^0.63);
   psi_2=exp(-1.87*tan(beta/2).^1.22);
   mag=H+5*log10(R.*delta)-2.5*log10((1-G)*psi_1+G*psi_2);
elseif length(planet)>6
   % g,k model
   g=planet(7);
   k=planet(8);
   mag=g+5*log10(delta)+2.5*k*log10(R);
elseif M==1
   mag=nan; return;
   switch planet
   case 0, g=-27; k=0.2;
   case 1, g=-0.36; k=0.2;
   case 2, g=-4.29; k=0.2;
   case 3, g=nan; k=0.2;
   case 4, g=-1.52; k=0.2;
   case 5, g=-9.25; k=0.2;
   case 6, g=-8.88; k=0.2;
   case 7, g=-7.19; k=0.2;
   case 8, g=-6.87; k=0.2;
   case 9, g=-1.01; k=0.2;
   otherwise g=nan; k=0.2;
   end;
   mag=g+5*log10(delta)+2.5*k*log10(R);
end;


   