function [nous,etel,lask,dawn,dusk]=risetnew(jd,pl,pit,lev,kork,tz);

jd0=round(jd+tz/24)-0.5;
st0=sidertime(jd0)-pit*12/pi;
d=atan([6.96e+5 2440 6052 0 3397 71492 60268 25559 24764 1151]/149.6e6);

etel=0; t2=1; c=0;
while abs(etel-t2)>1/120 & c<5
   [ra,de,delta,p]=calcsolar(pl,jd0+etel/24,pit,lev,kork,0,0);
   t2=etel;
   etel=ra*12/pi-st0;
   while etel+tz<0 etel=etel+24; end;
   while etel+tz>24 etel=etel-24; end;
   etel=etel/1.0027378;
   c=c+1;
end;

%amospheric and parallactic effects taken into account (use geomertic coords)
h0=-0.0098902;
if pl==3 
   h0=h0+p-atan(1738./delta);
elseif ~isvector(pl) 
   h0=h0-d(pl+1);
end;
cosha=(sin(h0)-sin(lev)*sin(de))./(cos(lev)*cos(de));
ha=sidertime(jd0+etel/24)*pi/12-ra-pit;
alt=asin(sin(lev).*sin(de)+cos(lev).*cos(de).*cos(ha));
if abs(cosha)<=1
   h=acos((abs(cosha)<=1).*cosha)*12/pi;
   nous=etel-h/1.0027378;
   lask=etel+h/1.0027378;
   if nous+tz<0 nous=nous+24; end;
   if lask+tz>24 lask=lask-24; end;   
else
   nous=sign(cosha)*inf;
   lask=sign(cosha)*inf;
end;

t2=nous; nous=nous+1; alt0=alt; cosha=0; c=0;
while abs(nous-t2)>1/120 & c<10 & abs(cosha)<=1;
   [ra,de,delta,p]=calcsolar(pl,jd0+nous/24,pit,lev,kork,0,0);
   ha=sidertime(jd0+nous/24)*pi/12-ra-pit;
   cosha=(sin(h0)-sin(lev)*sin(de))./(cos(lev)*cos(de));
   alt1=asin(sin(lev).*sin(de)+cos(lev).*cos(de).*cos(ha));
   if (c==0) dt=1; else dt=(alt1-h0).*dt./(alt0-alt1); end;
   t2=nous;
   nous=nous+dt;
   alt0=alt1;
   c=c+1;
end;
if abs(cosha)>1 nous=sign(cosha)*inf; elseif abs(nous-t2)>1/120 nous=nan; end;

t2=lask; lask=lask+1; alt0=alt; cosha=0; c=0;
while abs(lask-t2)>1/120 & c<10 & abs(cosha)<=1;
   [ra,de,delta,p]=calcsolar(pl,jd0+lask/24,pit,lev,kork,0,0);
   ha=sidertime(jd0+lask/24)*pi/12-ra-pit;
   cosha=(sin(h0)-sin(lev)*sin(de))./(cos(lev)*cos(de));
   alt1=asin(sin(lev).*sin(de)+cos(lev).*cos(de).*cos(ha));
   if (c==0) dt=1; else dt=(alt1-h0).*dt./(alt0-alt1); end;
   t2=lask;
   lask=lask+dt;
   alt0=alt1;
   c=c+1;
end;
if abs(cosha)>1 lask=sign(cosha)*inf; elseif abs(lask-t2)>1/120 lask=nan; end;

if pl==0 & 0
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
