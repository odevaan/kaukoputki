function nro=getmess;

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='normal';
txt={'Messier numero'};
a={' '};
nro=0;
while ~isempty(a) & ~(nro>0 & nro<111)
  a=inputdlg(txt,'Messier kohde',[1 30],a,AddOpts);
  if ~isempty(a) 
     nro=fix(str2double(a{1}));
     if ~(nro>0 & nro<111) | isnan(nro)
        uiwait(errordlg('Virhe Messier numerossa!','Messier kohde','replace'));
     end; 
  end;   
end;
 
