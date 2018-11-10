function [ra,de]=getcoord(ra,de,epochst);

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='normal';
txt={['Rektaskensio, ' epochst],['Deklinaatio, ' epochst]};
a={dec2hms(ra*12/pi),dec2dms(de*180/pi)};
ra=''; de='';
while (isempty(ra) | isempty(de)) & ~isempty(a)
  a=inputdlg(txt,'Kiinteät koordinaatit',[1 30],a,AddOpts);
  if length(a)==2
    if ~isempty(a{1}) ra=str2dec(a{1})*pi/12; end;
    if ~isempty(a{2}) de=str2dec(a{2})*pi/180; end;
    if isempty(ra) | isempty(de)
       uiwait(errordlg('Virhe koordinaateissa!','Koordinaatit','replace'));
    end; 
  end;   
end;
 
