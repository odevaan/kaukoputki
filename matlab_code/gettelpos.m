function [hatel,ratel,detel]=gettelpos(st0,pit,lev,paine,temp,Mra,Mde,Nstep,IH,ID,CH,MA,ME,NP,TF,FF,DF);
%
%function [hatel,ratel,detel]=gettelpos(st0,pit,lev,paine,temp,Mra,Mde,Nstep,IH,ID,CH,MA,ME,NP,TF,FF,DF)

[hatel,detel]=telpos(Mra,Mde,Nstep,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
[hatel,detel]=atm2equ(hatel,detel,lev,paine,temp);
ratel=mod(st0*pi/12-(pit+hatel),2*pi);