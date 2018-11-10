function [Hl,del]=equ2local(H,de,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
%function [Hl,del]=equ2local(H,de,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);

if isempty(IH) IH=0; end;
if isempty(ID) ID=0; end;
if isempty(CH) CH=0; end;
if isempty(MA) MA=0; end;
if isempty(ME) ME=0; end;
if isempty(NP) NP=0; end;
if isempty(TF) TF=0; end;
if isempty(FF) FF=0; end;
if isempty(DF) DF=0; end;

deltaH=IH-MA*cos(H).*tan(de)+CH./cos(de)+ME*sin(H).*tan(de)+NP*tan(de)+TF*cos(lev)*sin(H)./cos(de)-DF*(cos(lev)*cos(H)+sin(lev)*tan(de));
deltad=ID+MA*sin(H)+ME*cos(H)+TF*(cos(lev)*cos(H).*sin(de)-sin(lev)*cos(de))+FF*cos(H);
Hl=H+deltaH;
del=de+deltad;
