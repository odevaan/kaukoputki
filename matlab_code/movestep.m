%script movestep
%movedir = 
%'N' => North
%'S' => South
%'E' => East
%'W' => West

if checknano
   jde=jd+deltat(jd)/86400;
   if apparent 
      [dphi,deps]=nutation(jde);
      epsilon=ecliptic(jde);
      st0=sidertime(jd,dphi,epsilon);
   else
      st0=sidertime(jd);
   end;

   [hatel,ratel,detel]=gettelpos(st0,pit,lev,paine,temp,Mra,Mde,Nstep,IH,ID,CH,MA,ME,NP,TF,FF,DF);
   destep=abs(str2double(get(hmovestep,'string')))*pi/10800;
   if abs(cos(detel))>0.00003 
      rastep=destep/cos(detel);
      if rastep>2*pi rastep=0; end;
   else
      rastep=0;
   end

   switch movedir
   case 'N',
      detel=detel+destep;   
   case 'S',
      detel=detel-destep;
   case 'E',
      hatel=hatel-rastep;
   case 'W',
      hatel=hatel+rastep;
   end;
   ratel=mod(st0*pi/12-(pit+hatel),2*pi);

   ra0=ratel;
   de0=detel;
   type=1;
   recalc;
   kohdista; 
end;

