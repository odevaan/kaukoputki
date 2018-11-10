function [H,de]=local2equ(Hl,del,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
%function [H,de]=local2equ(Hl,del,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);

if isempty(IH) IH=0; end;
if isempty(ID) ID=0; end;
if isempty(CH) CH=0; end;
if isempty(MA) MA=0; end;
if isempty(ME) ME=0; end;
if isempty(NP) NP=0; end;
if isempty(TF) TF=0; end;
if isempty(FF) FF=0; end;
if isempty(DF) DF=0; end;

H=Hl; de=del;
for k=1:5;
  deltaH=IH-MA*cos(H).*tan(de)+ME*sin(H).*tan(de)+CH./cos(de)+NP*tan(de)+TF*cos(lev)*sin(H)./cos(de)-DF*(cos(lev)*cos(H)+sin(lev)*tan(de));
  deltad=ID+MA*sin(H)+ME*cos(H)+TF*(cos(lev)*cos(H).*sin(de)-sin(lev)*cos(de))+FF*cos(H);
  H=Hl-deltaH;
  de=del-deltad;
end;
