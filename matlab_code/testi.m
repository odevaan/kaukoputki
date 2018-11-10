minH=-220*pi/180;
maxH=220*pi/180;
deltaH=ha-ha0+2*pi*[-1 0 1];
[foo,ind]=min(abs(deltaH));
deltaH=deltaH(ind);
if abs(deltaH)==pi
   deltaH=pi*(1-2*(ha0>0));
end;
if ha0<minH+pi & ha<minH+2*pi+0.017 & ha>ha0+pi
   deltaH=deltaH+2*pi;
elseif ha0>maxH-pi & ha>maxH-2*pi-0.017 & ha<ha0-pi
   deltaH=deltaH-2*pi;
end;
ha=ha0+deltaH;
