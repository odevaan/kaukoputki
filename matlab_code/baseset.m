%Perusasetukset

global nanook stopit timeorig isok;
AddOpts.Interpreter='tex';AddOpts.Resize='off';AddOpts.WindowStyle='normal';
pit=str2dec('-29°59''48"')*pi/180;
lev=str2dec('62°43''38"')*pi/180;
tz=2;
kork=155;
paine=1013;
temp=-10;
elem=2451545*[1 0 0 0 0 0]';
type=5;nro=45;[ra0,de0,data]=read(type,nro); pmra=0; pmde=0;
type_=type; nro_=nro; ra0_=ra0; de0_=de0; pmra_=pmra; pmde_=pmde;
tags=0;
refok=0;
cputime=1;
apparent=0;
epochofdate=0;
timeorig='time';
Mra=18800;Mde=14100;Nstep=512;
minH=-220*pi/180; maxH=220*pi/180;
IH=[]; ID=[]; MA=[]; ME=[]; CH=[]; NP=[]; TF=[]; FF=[]; DF=[];
elemname='';
ename={''};
guidedir='d:\guide7\';

configfile='kaukoputki.cfg';
h=fopen(configfile,'r');
if h~=-1 
   fclose(h);
   load(configfile,'-MAT'); 
end;
nanook=checknano;
