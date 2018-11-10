if ~tags findtags; end;
if cputime
   t=clock;
   y=t(1); m=t(2); d=t(3); ut=t(4)+t(5)/60+t(6)/3600-tz;
else
   [y,m,d]=str2date(get(hdate,'String'));
   ut=str2dec(get(htime,'String'))-tz;
end;
jd=julian(y,m,d,ut);

jde=jd+deltat(jd)/86400;
if apparent 
   [dphi,deps]=nutation(jde);
   epsilon=ecliptic(jde);
   st0=sidertime(jd,dphi,epsilon);
else
   st0=sidertime(jd);
end;

if ~epochofdate
   ste=get(hepoch,'String');
   if strcmp(ste,'Date') 
      ste='2000.01.01.5'; 
   end;
   [y,m,d]=str2date(ste);
   epoch=julian(y,m,d);
else
   epoch=jd;
end;

if ~isempty(nro) & ~isempty(type)
  ra=ra0;
  de=de0;
else
   nro=nro_;
   type=type_;
   ra0=ra0_;
   de0=de0_;
   pmra=pmra_;
   pmde=pmde_;
   capt=capt_;
   ra=ra0;
   de=de0;
end;

guideread=0;
if get(hguide,'value')
   f=fopen([guidedir 'slew.dat']);
   if f>0
      while ~feof(f)
         str=fgetl(f);
         if str(1)=='R' 
            ra0=sscanf(str(2:end),'%f')*pi/180; 
            guideread=guideread+1;
         end;
         if str(1)=='D' 
            de0=sscanf(str(2:end),'%f')*pi/180; 
            guideread=guideread+1;
         end;
      end;
      fclose(f);
      if guideread>=2
         % Guide export J2000.0 positions
         % Jostain helvetin syystä tulee yksi prekessio liikaa
         % jos EOD on päällä ja Guidesta tulee suuntaus!
         
         %disp(['From Guide: ' dec2hms(ra0*12/pi,5) dec2dms(de0*180/pi,5)]);
         ra=ra0; de=de0;
         delete([guidedir 'slew.dat']);
         type=1; nro=0; data={'','Guiden asetus'};
         [ra,de]=precess(ra,de,2451545.0,epoch);
         if apparent [ra,de]=apparentpos(ra,de,jde); end;
         kohdista;
         ra=ra0; de=de0;
      end;
   end;
end;   

%paikat J2000.0, paitsi planeetoille epoch of date
switch type
case 1
   capt='Kiinteät koordinaatit';
case 2
   capt=sprintf('HR%i',nro);
   ra=ra+pmra*(jd-2451545)/365.25;
   de=de+pmde*(jd-2451545)/365.25;
case 3
   capt=sprintf('NGC%i',nro);
case 4
   capt=sprintf('IC%i',nro);
case 5
   capt=sprintf('M%i',nro);
case {10,11}
   if (~isvector(nro) & nro>0 & nro<11) | length(nro)>=6
      if nro==3
         [ra,de,delta,p,elong,phase]=moon(jde,0);
         data={'Etäis. [km]|elong.|vaihe ',sprintf('%11.0f|%6.2f|%6.2f',delta,elong*180/pi,phase*180/pi)};
         capt='Kuu';
      else
         [ra,de,delta,p,elong,phase,mag]=geompos(jde,nro,0);
         data={'Etäis. [AU]|elong.|vaihe |mag  ',sprintf('%11.6f|%6.2f|%6.2f|%5.1f',delta,elong*180/pi,phase*180/pi,mag)};
         if type==10 & nro<10 
            capt=planet{nro};
         end;
      end;
      [ra,de]=topocpos(ra,de,p,st0,pit,lev,kork);
   end;
end;

if type>0
   if apparent [ra,de]=apparentpos(ra,de,jde); end;
   if type==10 
      [ra,de]=precess(ra,de,jd,epoch); 
   else
      [ra,de]=precess(ra,de,2451545.0,epoch);
   end;
end;

if type==10
   [nous,etel,lask]=risetpl(jd,nro,pit,lev,kork,tz);
else
   [nous,etel,lask]=riset(jd,ra,de,pit,lev,kork,tz);
end;
[nous,etel,lask]=risetst(nous+tz,etel+tz,lask+tz);

[y,m,d,t]=date(jd+tz/24);
set(hdate,'String',sprintf('%1.0f.%02.0f.%02.0f',y,m,d));
set(htime,'String',dec2hms(t));
set(hjulian,'String',sprintf('%1.4f',jd));
set(hta,'String',dec2hms(mod(st0-pit*12/pi,24)));
if epochofdate
   set(hepoch,'String','Date');
else
   [y,m,d]=date(epoch);
   set(hepoch,'String',sprintf('%1.0f.%02.0f.%02.0f',y,m,d));
end;
set(hpit,'String',dec2dms(pit*180/pi));
set(hlev,'String',dec2dms(lev*180/pi));
set(hkork,'String',sprintf('%1.0f',kork));
set(hpaine,'String',sprintf('%1.0f',paine));
set(htemp,'String',sprintf('%1.0f',temp));
set(htz,'String',num2str(tz));
set(happarent,'Value',apparent);
set(hcputime,'Value',cputime);
set(hepochofdate,'Value',epochofdate);
if type>0
  ha=hourangle(ra,st0,pit);
  [ats,alt]=equ2horiz(ha,de,lev);
  set(hcapt,'String',capt);
  set(hra,'String',dec2hms(ra*12/pi,6));
  set(hde,'String',dec2dms(de*180/pi,6));
  set(hha,'String',dec2hms(ha*12/pi));
  set(hat,'String',sprintf('%6.3f°',ats*180/pi));
  set(hal,'String',sprintf('%6.3f°',alt*180/pi));
  set(hno,'String',nous);
  set(het,'String',etel);
  set(hla,'String',lask);
else
  set(hcapt,'String','Tuntematon');
  set(hra,'String','-');     
  set(hde,'String','-');      
  set(hha,'String','-');
  set(hat,'String','-');
  set(hal,'String','-');
  set(hno,'String','-');
  set(het,'String','-');
  set(hla,'String','-');
end;   
set(hda,'String',data);
ra_=ra; de_=de; ra0_=ra0; de0_=de0; pmra_=pmra; pmde_=pmde; type_=type; nro_=nro; capt_=capt;

[raa,dea,delta,p]=geompos(jde,0,0);
[raa,dea]=topocpos(raa,dea,p,st0,pit,lev,kork);
if apparent [raa,dea]=apparentpos(raa,dea,jde); end;
if ~epochofdate [raa,dea]=precess(raa,dea,jd,epoch); end;
haa=hourangle(raa,st0,pit);
[atsa,alta]=equ2horiz(haa,dea,lev);
[nous,etel,lask,dawn,dusk]=risetpl(jd,0,pit,lev,kork,tz);
[nous,etel,lask,dawn,dusk]=risetst(nous+tz,etel+tz,lask+tz,dawn+tz,dusk+tz);
set(hraa,'String',dec2hms(raa*12/pi));      
set(hdea,'String',dec2dms(dea*180/pi));
set(hhaa,'String',dec2hms(haa*12/pi));
set(hata,'String',sprintf('%6.3f°',atsa*180/pi));
set(hala,'String',sprintf('%6.3f°',alta*180/pi));
set(hnoa,'String',nous);
set(heta,'String',etel);
set(hlaa,'String',lask);
set(hdawn,'String',dawn);
set(hdusk,'String',dusk);

[ram,dem,delta,p]=moon(jde,0);
[ram,dem]=topocpos(ram,dem,p,st0,pit,lev,kork);
if apparent [ram,dem]=apparentpos(ram,dem,jde); end;
if ~epochofdate [ram,dem]=precess(ram,dem,jd,epoch); end;
ham=hourangle(ram,st0,pit);
[atsm,altm]=equ2horiz(ram,dem,lev);
[nous,etel,lask]=risetpl(jd,3,pit,lev,kork,tz);
[nous,etel,lask]=risetst(nous+tz,etel+tz,lask+tz);
set(hram,'String',dec2hms(ram*12/pi));
set(hdem,'String',dec2dms(dem*180/pi));
set(hham,'String',dec2hms(ham*12/pi));
set(hatm,'String',sprintf('%6.3f°',atsm*180/pi));
set(halm,'String',sprintf('%6.3f°',altm*180/pi));
set(hnom,'String',nous);
set(hetm,'String',etel);
set(hlam,'String',lask);

if nanook
  [hatel,detel]=telpos(Mra,Mde,Nstep,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
  [hatel,detel]=atm2equ(hatel,detel,lev,paine,temp);
  ratel=mod(st0*pi/12-(pit+hatel),2*pi);
  [ratel,detel]=precess(ratel,detel,2451545.0,epoch);
  if apparent [ratel,detel]=apparentpos(ratel,detel,jde); end;
  set(htra,'String',dec2hms(ratel*12/pi,5));
  set(htde,'String',dec2dms(detel*180/pi,5));
  [ratel,detel]=precess(ratel,detel,epoch,jd);
  f=fopen([guidedir 'slew_out.dat'],'w');
  if f>0
     %disp(['To Guide: ' dec2hms(ratel*12/pi,5) dec2dms(detel*180/pi,5)]);
     fprintf(f,' %10.6f %10.6f\n',ratel*180/pi,detel*180/pi);
     fclose(f);
  end
  
  %ratelv=[ratelv ratel]; detelv=[detelv detel]; tv=[tv toc]; figure(2); plot(tv-tv(1),[ratelv-ratelv(1); detelv-detelv(1)]*206265); figure(1);
end

