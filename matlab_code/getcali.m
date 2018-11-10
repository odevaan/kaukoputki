function [ha,de,hal,del,IH,ID,CH,MA,ME,NP,TF,FF,DF]=getcali(ha,de,hal,del,Mra,Mde,Nstep,IH,ID,CH,MA,ME,NP,TF,FF,DF,pit,lev,paine,temp,tz,apparent,isnew);
%
%function [ha,de,hal,del,IH,ID,CH,MA,ME,NP,TF,FF,DF]=getcali(ha,de,hal,del,Mra,Mde,Nstep,IH,ID,CH,MA,ME,NP,TF,FF,DF,pit,lev,paine,temp,tz,apparent,isnew);
%
%Uses J2000.0 positions with proper motions for calibration!

calihrs=[15 21 39 168 264 337 403 553 603 617 911 915 936 1017 1165 1203 1220 1457 1577 1708 1790 1791 2061 2088 2095 2286 2421 2845 2890 2943 2990 3873 3982 4057 4295 4301 4357 4534 4554 4905 4915 4932 5054 5191 5235 5340 5506 5793 5854 6132 6148 6212 6536 6556 6603 6705 7001 7235 7525 7528 7557 7796 7924 7949 8162 8308 8650 8775 8781];
tIH=findobj('Tag','txtIH'); chIH=findobj('Tag','chIH');
tID=findobj('Tag','txtID'); chID=findobj('Tag','chID');
tCH=findobj('Tag','txtCH'); chCH=findobj('Tag','chCH');
tMA=findobj('Tag','txtMA'); chMA=findobj('Tag','chMA');
tME=findobj('Tag','txtME'); chME=findobj('Tag','chME');
tNP=findobj('Tag','txtNP'); chNP=findobj('Tag','chNP');
tTF=findobj('Tag','txtTF'); chTF=findobj('Tag','chTF');
tFF=findobj('Tag','txtFF'); chFF=findobj('Tag','chFF');
tDF=findobj('Tag','txtDF'); chDF=findobj('Tag','chDF');
h=findobj('Tag','calipopup');
calihr=calihrs(get(h,'Value'));
if calihr>0 & isnew
  t=clock;
  jd=julian(t(1),t(2),t(3),t(4)+t(5)/60+t(6)/3600-tz);
  jde=jd+deltat(jd)/86400;
  if apparent
    [ra,de]=apparentpos(ra,de,jde);
    [dphi,deps]=nutation(jde);
    epsilon=ecliptic(jde);
    st0=sidertime(jd,dphi,epsilon);
  else
    st0=sidertime(jd);
  end;
  [ra,de(end+1),hrname,nro,pmra,pmde]=read(2,calihr);
  ra=ra+pmra*(jd-2451545)/365.25;
  de(end)=de(end)+pmde*(jd-2451545)/365.25;
  ha(end+1)=hourangle(ra,st0,pit);
  [hat,det]=telpos(Mra,Mde,Nstep,lev,0,0,0,0,0,0,0,0,0);
  [hal(end+1),del(end+1)]=atm2equ(hat,det,lev,paine,temp);
  hast=[dec2hms(ha(end)*12/pi,5) ' ' dec2hms(hal(end)*12/pi,5)];
  dest=[dec2dms(de(end)*180/pi,5) ' ' dec2dms(del(end)*180/pi,5)];
  h=findobj('Tag','calislist');
  st=get(h,'String');
  st{end+1}=[hast '|' dest];
  set(h,'String',st);
end;  

ha=ha(:); de=de(:); hal=hal(:); del=del(:);
save calistars.mat ha de hal del;  
N=length(ha);
if N>0
  Mh=zeros(N,0); Md=zeros(N,0);
  if get(chIH,'Value') Mh(:,end+1)=ones(N,1); IH=0; end;
  if get(chID,'Value') Md(:,end+1)=ones(N,1); ID=0; end;
  if get(chCH,'Value') Mh(:,end+1)=1./cos(de); CH=0; end;
  if get(chMA,'Value') Mh(:,end+1)=-cos(ha).*tan(de); Md(:,end+1)=sin(ha); MA=0; end;
  if get(chME,'Value') Mh(:,end+1)=sin(ha).*tan(de); Md(:,end+1)=cos(ha); ME=0; end;
  if get(chNP,'Value') Mh(:,end+1)=tan(de); NP=0; end;
  if get(chTF,'Value') Mh(:,end+1)=cos(lev)*sin(ha)./cos(de); Md(:,end+1)=cos(lev)*cos(ha).*sin(de)-sin(lev)*cos(de); TF=0; end;
  if get(chFF,'Value') Md(:,end+1)=cos(ha); FF=0; end;
  if get(chDF,'Value') Mh(:,end+1)=-cos(lev)*cos(ha)-sin(lev)*tan(de); DF=0; end;
  [ha2,de2]=local2equ(hal,del,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
  if prod(size(Mh)) 
     xh=Mh\atan2(sin(ha2-ha),cos(ha2-ha));
  end;
  if prod(size(Md)) 
     xd=Md\(de2-de);
  end;
  indh=1; indd=1;
  if get(chIH,'Value') IH=xh(indh); indh=indh+1; end;
  if get(chID,'Value') ID=xd(indd); indd=indd+1; end;
  if get(chCH,'Value') CH=xh(indh); indh=indh+1; end;
  if get(chMA,'Value') MA=(xh(indh)+xd(indd))/2; indh=indh+1; indd=indd+1; end;
  if get(chME,'Value') ME=(xh(indh)+xd(indd))/2; indh=indh+1; indd=indd+1; end;
  if get(chNP,'Value') NP=xh(indh); indh=indh+1; end;
  if get(chTF,'Value') TF=(xh(indh)+xd(indd))/2; indh=indh+1; indd=indd+1; end;
  if get(chFF,'Value') FF=xd(indd); indd=indd+1; end;
  if get(chDF,'Value') DF=xh(indh); indh=indh+1; end;
  [ha2,de2]=local2equ(hal,del,lev,IH,ID,CH,MA,ME,NP,TF,FF,DF);
  dha=206265*atan2(sin(ha2-ha),cos(ha2-ha)).*cos(de); dde=206265*(de2-de);
  if any([dha;dde]>60)
     dha=dha/60; dde=dde/60; st='min';
  else st='sek'; end;
  plot(dha,dde,'x');
  xlabel(['\Delta\alpha [' st ']']);
  ylabel(['\Delta\delta [' st ']']);
  title('Otoksen kalibrointivirhe');
end;
set(tIH,'String',num2str(IH*206265));
set(tID,'String',num2str(ID*206265));
set(tCH,'String',num2str(CH*206265));
set(tMA,'String',num2str(MA*206265));
set(tME,'String',num2str(ME*206265));
set(tNP,'String',num2str(NP*206265));
set(tTF,'String',num2str(TF*206265));
set(tFF,'String',num2str(FF*206265));
set(tDF,'String',num2str(DF*206265));
  
