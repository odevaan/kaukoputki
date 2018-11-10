function [nous,etel,lask]=nouslask(jd,pl,pit,lev,kork);

jd0=fix(jd-0.5)+0.5
stg=sidertime(jd);
st0=sidertime(jd0)-pit*12/pi;
d=atan([6.96e+5 2440 6052 1738 3397 71492 60268 25559 24764 1151]/149.6e6);
dec2hms(st0)
t=zeros(1,3); tp=24*ones(1,3); c=0;
while all(abs(t-tp)>1/3600) & c<10
  if pl==3
    [ra,de,delta,p]=moon(jd0+t/24);
    h0=0.7275*p-0.0098902;
  else
    [ra,de,delta,p]=geompos(jd0+t/24,pl,0);
    h0=-0.0098902;
    if ~isvector(pl) h0=h0-d(pl+1); end;
  end;
  [ra,de]=topocpos(ra,de,p,stg,pit,lev,kork);
  cosha=(sin(h0)-sin(lev)*sin(de))./(cos(lev)*cos(de));
  h=acos((abs(cosha)<=1).*cosha)*12/pi;
  tp=t;
  t=(ra*12/pi-st0+(-1:1).*h)/1.0027378
  c=c+1;
end;
if abs(cosha(1))>1 nous=nan; else nous=t(1); end;
etel=t(2);
if abs(cosha(3))>1 lask=nan; else lask=t(3); end;
