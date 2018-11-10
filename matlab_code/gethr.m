function nro=gethr;

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='normal';
txt={'HR (The Bright Star Catalog) numero tai nimi'};
a={' '};
nro=0;
while ~isempty(a) & ~(nro>0 & nro<9111)
  a=inputdlg(txt,'HR',[1 30],a,AddOpts);
  if ~isempty(a) 
     nro=fix(str2double(a{1}));
     if isnan(nro)
        nro=a{1};
     elseif ~(nro>0 & nro<9111)
        uiwait(errordlg('Virhe HR numerossa!','HR kohde','replace'));
     end; 
  end;   
end;
 
