function nro=getic;

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='normal';
txt={'IC (The Integrated Catalog) numero'};
a={' '};
nro=0;
while ~isempty(a) & ~(nro>0 & nro<5387)
  a=inputdlg(txt,'IC kohde',[1 30],a,AddOpts);
  if ~isempty(a) 
     nro=fix(str2double(a{1}));
     if ~(nro>0 & nro<5387) | isnan(nro)
        uiwait(errordlg('Virhe IC numerossa!','IC kohde','replace'));
     end; 
  end;   
end;
 
