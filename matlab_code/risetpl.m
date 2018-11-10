function [nous,etel,lask,dawn,dusk]=risetpl(jd,pl,pit,lev,kork,tz);

jd0=round(jd+tz/24)-0.5;
stg=sidertime(jd);
st0=sidertime(jd0)-pit*12/pi;
d=atan([6.96e+5 2440 6052 1738 3397 71492 60268 25559 24764 1151]/149.6e6);
t=zeros(1,3); tp=24*ones(1,3); c=0;
while all(abs(t-tp)>1/120) & c<10
  if ~isvector(pl) & pl==3
    [ra,de,delta,p]=moon(jd0+t/24,0);
    h0=p-atan(1738./delta)-0.0098902;
  else
    [ra,de,delta,p]=geompos(jd0+t/24,pl,0);
    h0=-0.0098902;
    if ~isvector(pl) h0=h0-d(pl+1); end;
  end;
  cosha=(sin(h0)-sin(lev)*sin(de))./(cos(lev)*cos(de));
  h=acos((abs(cosha)<=1).*cosha)*12/pi;
  tp=t;
  t=ra*12/pi-st0+(-1:1).*h;
  if t<0 t=t+24; elseif t>24 t=t-24; end;
  t=t/1.0027378;
  c=c+1;
end;
if abs(cosha(1))>1 nous=sign(cosha(1))*inf; else nous=t(1); end;
etel=t(2);
if abs(cosha(3))>1 lask=sign(cosha(3))*inf; else lask=t(3); end;

if pl==0
   cosha=-(0.2079+sin(lev)*sin(de))./(cos(lev)*cos(de));
   h=acos((abs(cosha)<=1).*cosha)*12/pi;
   if abs(cosha(1))>1 dawn=sign(cosha(1))*inf; else dawn=etel-h(1); end;
   if abs(cosha(3))>1 dusk=sign(cosha(3))*inf; else dusk=etel+h(3); end;
end;
