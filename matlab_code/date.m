function [y,m,d,ut]=date(jd,n);
%[y,m,d,ut]=date(jd);
%[date,time]=date(jd,n);
%
%Calculates year y, month m, day d and optional universal time ut (hours)
%of julian date jd. Optionally calculates date in string form
%year/month/day and optional time in form hours/min/sec. 
%Optional n is used as number of decimals displayed in day or time.
%
%[Meeus, Astronomical algorithms, p.59-66, Willmann-Bell (1991)]
%
%P.Paakkonen (2000)

if nargin<2 n=4; end;
jd=jd+0.5;
Z=fix(jd);
F=jd-Z;
a=fix((Z-1867216.25)/36524.25);
A=Z+(Z>2299160).*(1+a-fix(a/4));
B=A+1524;
C=fix((B-122.1)/365.25);
D=fix(365.25*C);
E=fix((B-D)/30.6001);
d=B-D-fix(30.6001*E)+F;
m=E-1-12*(E>13);
y=C-4715-(m>2);
if nargout>3
  dt=d;
  d=fix(d);
  ut=24*(dt-d);
elseif nargout<3
  yt=y;
  K=prod(size(jd));
  if nargout<2
    eval(sprintf('y=sprintf(''%%5.0f/%%2.0f/%%%1.0f.%1.0ff'',yt(1),m(1),d(1));',n+3,n));
    for k=2:K
      eval(sprintf('y(k,:)=sprintf(''%%5.0f/%%2.0f/%%%1.0f.%1.0ff'',yt(k),m(k),d(k));',n+3,n));
    end;
  else
    mt=m;
    y=sprintf('%5.0f/%2.0f/%2.0f',yt(1),mt(1),fix(d(1)));
    m=dec2hms(24*(d(1)-fix(d(1))),n);
    for k=2:K
      y(k,:)=sprintf('%5.0f/%2.0f/%2.0f',yt(k),mt(k),fix(d(k)));
      m(k,:)=dec2hms(24*(d(k)-fix(d(k))),n);
    end;
  end;
end;
