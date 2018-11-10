%Script kohdista.
%update;
speed=6000;
if ~type
   warndlg('Mit‰‰n kunnollista kohdetta ei ole m‰‰ritelty!','Huom!','modal');
   return;
end;
if ~refok
   warndlg('Referenssiajoa tai kalibrointia ei ole suoritettu!','Huom!','modal');
   return;
end;
if de < -50*pi/180 | de > pi
   warndlg('Deklinaatioakselia voi olla vain v‰lill‰ -50∞ - +90∞!','Huom!','modal');
   return;
end;
d=acos(cos(raa-ra)*cos(dea)*cos(de)+(sin(dea)*sin(de))); 
if d<0.07
   warndlg({'Kohde alle 4∞ et‰isyydell‰ Auringosta!','Kohdista Aurinkoon k‰sipelill‰.'},'Vaaran paikka!','modal');
   return;
end;
if alt < 0
   if isequal(questdlg('Kohde horisontin alapuolella! Haluatko jatkaa?','Huom!','Kyll‰','Ei','Kyll‰'),'Ei') return; end;
end;

%back to J2000.0
ram=ra;
dem=de;
if apparent
   [ram,dem]=astrometricpos(ram,dem,jde);
end
if ~epochofdate
   [ram,dem]=precess(ram,dem,epoch,2451545.0);
end
ham=hourangle(ram,st0,pit);

set(htra,'String','-');
set(htde,'String','-');
[ham,dem]=equ2atm(ham,dem,lev,paine,temp);
if ~movetel(ham,dem,Mra,Mde,Nstep,speed,minH,maxH,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
   [ham,dem]=telpos(Mra,Mde,Nstep,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
end;
[ham,dem]=atm2equ(ham,dem,lev,paine,temp);
set(htra,'String',dec2hms(mod(st0-(pit+ham)*12/pi,24),5));
set(htde,'String',dec2dms(dem*180/pi,5));

