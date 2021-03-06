function res=movetel(ha,de,Mra,Mde,Nstep,speed,minH,maxH,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF)
%function res=movetel(ha,de,Mra,Mde,Nstep,speed,minH,maxH,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF)
%
%Siirt�� kaukoputken suuntaan ha,de (radiaaneina).
%T�m� koodi on osin FM Marjut Ristolan pro gradu- ty�st� v. 2000.

global stopit;
stopit=0;   % stoppinappulan tila nollaksi
t0=cputime; % funktion aloitusaika muistiin
hdelay=1.0; % aika (s), jonka tuntiakseli on pys�hdyksiss�
% kohteeseen siirtymisen j�lkeen ennen speed controliin siirtymist�

[ha0,de0,ha0step,de0step]=telpos(Mra,Mde,Nstep,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
nanocom('SetReg',12102,de0step); % actual- arvot nominaalirekistereihin
nanocom('SetReg',13102,ha0step);

% siirryt��n jalustan koordinaatistoon ja
% lasketaan mihin suuntaan pit�� siirty� jotta
% mekaaniset rajat maxH=+220 ja minH=-220 eiv�t ylity
[ha,de]=equ2local(ha,de,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
deltaH=ha-ha0+2*pi*[-1 0 1]; %minH<ha0<maxH, -180<ha<+180
[foo,ind]=min(abs(deltaH));
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
% lasketaan steppien m��r�t
hastep=round(Mra*Nstep*(ha+1.0027378*(hdelay+cputime-t0)*2*pi/86400)/(2*pi));
destep=-round(Mde*Nstep*de/(2*pi));

nanocom('SetBit',12100,1,9);    % Position control
nanocom('SetBit',13100,1,9);
nanocom('SetReg',12103,speed);  % asetetaan nopeudet
nanocom('SetReg',13103,speed);
nanocom('SetReg',12102,destep); % deklinaatioakselin nominaalipaikka 
nanocom('SetReg',13102,hastep); % tuntiakselin nominaalipaikka
%nanocom('SetOutput',101,1);     % Summeri p��lle.

haok=0; deok=0;
prevt=-1;
while (~haok | ~deok) & ~stopit
   if ~deok
     value1 = nanocom('GetBit',12100,0,1);
     if value1 
        nanocom('SetBit',12100,0,9);    % Speed control
        deok=1;
     end;
   end;
   if ~haok
     t=cputime; 
     if round(t)~=round(prevt)
        hastep=round(Mra*Nstep*(ha+1.0027378*(hdelay+t-t0)*2*pi/86400)/(2*pi));
        nanocom('SetReg',13102,hastep);
        prevt=t;
     end
     value2 = nanocom('GetBit',13100,0,1);
     if value2
        nanocom('SetBit',13100,0,9);    % Speed control
        haok=1;
     end;
   end;
   pause(0);
end
nanocom('SetOutput',101,0);     % Summeri pois p��lt�.
res=(haok & deok);
if ~res
   nanocom('SetBit',12100,0,9);    % Speed control
   nanocom('SetBit',13100,0,9);    % Speed control
   warndlg('Kohdistus ei onnistunut!','Huom!','modal');
else
   %warndlg('Kaikki OK!','Jess!','modal');
end

