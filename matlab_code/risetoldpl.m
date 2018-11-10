function [nous,etel,lask,dawn,dusk]=risetoldpl(jd,pl,pit,lev,kork,tz);

jd0=round(jd+tz/24)-0.5;
stg=sidertime(jd);
st0=sidertime(jd0)-pit*12/pi;
d=atan([6.96e+5 2440 6052 1738 3397 71492 60268 25559 24764 1151]/149.6e6);
t=zeros(1,3); t1=t; t2=24*ones(1,3); alt0=10; c=0;
while any(abs(t-t2)>1/120) & c<10
  if ~isvector(pl) & pl==3
    [ra,de,delta,p]=moon(jd0+t/24,0);
    h0=p-atan(1738./delta)-0.0098902;
  else
    [ra,de,delta,p]=geompos(jd0+t/24,pl,0);
    h0=-0.0098902;
    if ~isvector(pl) h0=h0-d(pl+1); end;
  end;
  ha=sidertime(jd0+t/24)*pi/12-ra-pit;
  alt1=asin(sin(lev).*sin(de)+cos(lev).*cos(de).*cos(ha));
  if (0) %sekanttimenetelmä nousuun ja laskuun, tökkii kulminointiajassa (div. by 0) 
     dt=(alt1-h0).*dt./(alt0-alt1);
     t2=t;
     t=t+dt;
     t(2)=ra(2)*12/pi-st0;
  else     
    cosha=(sin(h0)-sin(lev)*sin(de))./(cos(lev)*cos(de));
    h=acos((abs(cosha)<=1).*cosha)*12/pi;
    t2=t1;
    t1=t;
    t=ra*12/pi-st0+(-1:1).*h;
    while any(t+tz<0) t=t+24*(t+tz<0); end;
    while any(t+tz>24) t=t-24*(t+tz>24); end;
    t=t/1.0027378
    dt=0.1*ones(size(t));
  end;
  alt0=alt1; ha0=ha;
  c=c+1;
end;
if abs(cosha(1))>1 nous=sign(cosha(1))*inf; elseif abs(t(1)-t(1))>1/120 nous=nan; else nous=t(1); end;
if abs(t(2)-t1(2))>1/120 etel=nan; else etel=t(2); end;
if abs(cosha(3))>1 lask=sign(cosha(3))*inf; elseif abs(t(3)-t1(3))>1/120 lask=nan; else lask=t(3); end;

if pl==0
   t2=t+1;
   c=0;
   while any(abs(t-t2)>1/120) & c<5
     [ra,de,delta,p]=geompos(jd0+t/24,0,0);
     cosha=-(0.20791+sin(lev)*sin(de))./(cos(lev)*cos(de)); %-12°
     h=acos((abs(cosha)<=1).*cosha)*12/pi;
     t2=t;
     t=t(2)+(-1:1).*h;
     t=t/1.0027378;
     c=c+1;
   end;
   if abs(cosha(1))>1 dawn=sign(cosha(1))*inf; else dawn=etel-h(1); end;
   if abs(cosha(3))>1 dusk=sign(cosha(3))*inf; else dusk=etel+h(3); end;
end;
