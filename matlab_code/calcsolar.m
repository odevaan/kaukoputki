function [ra,de,delta,p,elon,phase,mag]=calcsolar(pl,jd,pit,lev,kork,apparent,topoc);

jde=jd+deltat(jd)/86400;
if apparent 
   [dphi,deps]=nutation(jde);
   epsilon=ecliptic(jde);
   st0=sidertime(jd,dphi,epsilon);
else
   st0=sidertime(jd);
end;
if pl==3
   [ra,de,delta,p,elong,phase,mag]=moon(jde,apparent);
else
   [ra,de,delta,p,elong,phase,mag]=geompos(jde,pl,apparent);
end;
if apparent [ra,de]=apparentpos(ra,de,jde); end;
if topoc [ra,de]=topocpos(ra,de,p,st0,pit,lev,kork); end;
