function [pl,name]=getelem(pl,name);

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='normal';
txt={'Nimi','Periheliaika [v kk pvm TD]','Eksentrisyys e','Perihelietäisyys a(1-e) [AU]','Inklinaatio i [°]','Perihelin argumentti \omega [°]','Nousevan solmun pit \Omega [°]'};
[y,m,d]=date(pl(1));
a={name,sprintf('%2.0f.%02.0f.%02.5f',y,m,d),num2str(pl(2),8),num2str(pl(3),8),num2str(pl(4)*180/pi,8),num2str(pl(5)*180/pi,8),num2str(pl(6)*180/pi,8)};
pl=nan*ones(6,1);
while any(isnan(pl)) & ~isempty(a)
  a=inputdlg(txt,'Rataelementit',[1 30],a,AddOpts);
  if length(a)==7
    name=a{1};
    [y,m,d]=str2date(a{2}); jd=julian(y,m,d); if ~isempty(jd) pl(1)=jd; else pl(1)=nan; end;
    pl(2)=str2double(a{3}); if pl(2)<0 | pl(2)>1 pl(2)=nan; end;
    pl(3)=str2double(a{4});
    pl(4)=str2double(a{5})*pi/180;
    pl(5)=str2double(a{6})*pi/180;
    pl(6)=str2double(a{7})*pi/180;
    if any(isnan(pl)) 
       uiwait(errordlg('Virhe rataelementeissä!','Rataelementit','replace'));
    end;
  end;   
end;
if isempty(a) pl=[]; name=''; end;
 
