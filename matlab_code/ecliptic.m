function epsilon=ecliptic(jde);
%function epsilon=ecliptic(jde);
%
%Calculates mean obliquity of the ecliptic on given
%instant jde. Uses expression of Laskar except
%here is period of 10000 years assumed for
%obliquity of ecliptic.
%
%[Meeus, J., Astronomical algorithms, 
%p. 135, Willmann-Bell (1991)]
%
%P. Paakkonen (2000)


t0=0.02505;
tm=0.97815;
t=(jde(:)'-2451545)/3652500-t0;
if any(abs(t)>tm)
  t=4*tm*rem(0.25*t/tm,1); 
  t=t+2*(abs(t)>tm).*(tm*sign(t)-t); 
  t=t+2*(abs(t)>tm).*(tm*sign(t)-t); 
end;
t=ones(11,1)*(t+t0); t(1,:)=1;
t=cumprod(t);

M=[84381.448 -4680.93 -1.55 1999.25 -51.38 -249.67 -39.05 7.12 27.87 5.79 2.45];
epsilon=(M*t)/206264.806247;
