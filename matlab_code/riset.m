function [nous,etel,lask]=riset(jd,ra,de,pit,lev,kork,tz);

jd0=round(jd+tz/24)-0.5;
stg=sidertime(jd);
st0=sidertime(jd0)-pit*12/pi;
if st0>12 st0=st0-24; elseif st0<-12 st0=st0+24; end;
cosha=-(0.00989+sin(lev)*sin(de))./(cos(lev)*cos(de));
h=acos((abs(cosha)<=1).*cosha)*12/pi;
t=(ra*12/pi-st0+(-1:1).*h)/1.0027378;
if abs(cosha)>1 nous=sign(cosha)*inf; else nous=t(1); end;
etel=t(2);
if abs(cosha)>1 lask=sign(cosha)*inf; else lask=t(3); end;

