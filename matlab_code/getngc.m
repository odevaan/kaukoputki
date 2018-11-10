function nro=getngc;

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='normal';
txt={'NGC (The New General Catalog) numero'};
a={' '};
nro=0;
while ~isempty(a) & ~(nro>0 & nro<7841)
  a=inputdlg(txt,'NGC kohde',[1 30],a,AddOpts);
  if ~isempty(a) 
     nro=fix(str2double(a{1}));
     if ~(nro>0 & nro<7841) | isnan(nro)
        uiwait(errordlg('Virhe NGC numerossa!','NGC kohde','replace'));
     end; 
  end;   
end;
 
