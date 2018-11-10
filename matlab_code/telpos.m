function [ha,de,hastep,destep]=telpos(Mra,Mde,Nstep,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
%function [ha,de,hastep,destep]=telpos(Mra,Mde,Nstep,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
%
%Hakee kaukoputken paikan ja k‰ytt‰‰ jalustakorjausta.

hastep = nanocom('GetReg',13109);
destep = nanocom('GetReg',12109);

ha=2*pi*hastep/(Mra*Nstep);
de=-2*pi*destep/(Mde*Nstep);
[ha,de]=local2equ(ha,de,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
