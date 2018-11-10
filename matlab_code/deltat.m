function dt=deltat(jd);
%function dt=deltat(jd);
%
%Calculates deltaT, the time difference TD-UT where
%TD is the dynamical (ephemeris) time and UT is the
%universal time. Thus, TD=UT+deltaT. TD is a uniform time,
%but UT needs some adjustments due the irregularities of
%Earth's rotation. In general, our civil live is based on 
%the UT but planetary aphemeris are based on TD.
%[Meeus, J., Astronomical algorithms, pp. 71-75, Willmann-Bell (1991)]
%
%dT for years >2000.0 are based on Earth Orientation Center
%measured data until 2006 and predicted data until 2025.
%
%P. Paakkonen (2000)

T=((1620:10:2000)-2000)/100;
DT=[124 85 62 48 37 26 16 10 9 10 11 11 12 13 15 16 17 17 13.7 12.5 12 7.5 5.7 7.1 7.9 1.6 -5.4 -5.9 -2.7 10.5 21.2 24 24.3 29.1 33.1 40.2 50.5 56.9 63.83];

t=(jd-2451545)/36525;
dt=zeros(size(t));

ind=find(t<-3.8);
if ~isempty(ind)
  dt(ind)=50.6+t(ind).*(67.5+t(ind)*22.5);
end;

ind=find(t>=-3.8 & t<=0);
if ~isempty(ind)
  dt(ind)=interp1(T,DT,t(ind),'spline');
end;

ind=find(t>0);
if ~isempty(ind)
  dt(ind)=63.83+15.9*t(ind);
end;
