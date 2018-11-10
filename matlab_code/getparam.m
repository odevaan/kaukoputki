function [Mra,Mde,Nstep,IH,ID,CH,MA,ME,NP,TF,FF,DF]=getparam(Mrai,Mdei,Nstepi,IHi,IDi,CHi,MAi,MEi,NPi,TFi,FFi,DFi)

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='modal';
txt={'Tuntiakselin v‰litys (18800)','Deklinaatioakselin v‰litys (14100)','Moottoreiden step/krs (512)','IH, tuntiaks. indeksivirhe','ID, dekl. akselin indeksivirhe','MA, tuntiaks. it‰.l‰nsi-virhe','ME, tuntiaks. kallistusvirhe','CH, kollimaatiovirhe','NP, akselien kohtisuoruusvirhe','TF, putken taipuma','FF, haarukan taipuma','DF, deklinaatioakselin taipuma'};
a={sprintf('%1.0f',Mrai),sprintf('%1.0f',Mdei),sprintf('%1.0f',Nstepi),num2str(IHi*206265),num2str(IDi*206265),num2str(CHi*206265),num2str(MAi*206265),num2str(MEi*206265),num2str(NPi*206265),num2str(TFi*206265),num2str(FFi*206265),num2str(DFi*206265)};
okay=0;
okay=~strcmp(questdlg('V‰‰r‰t vaihteistojen v‰lityssuhteet, askelm‰‰r‰t tai v‰‰r‰t jalustaparametrit johtavat kaukoputken virhesuuntaukseen. Haluatko jatkaa?','Varmistus','Kyll‰','En uskalla','Kyll‰'),'Kyll‰');
while ~isempty(a) & ~okay
  a=inputdlg(txt,'Konfiguraatio',[1 35],a,AddOpts);
  if length(a)==12
    Mra=str2double(a{1});
    Mde=str2double(a{2}); 
    Nstep=str2double(a{3});
    IH=str2double(a{4})/206265;
    ID=str2double(a{5})/206265;
    CH=str2double(a{6})/206265;
    MA=str2double(a{7})/206265;
    ME=str2double(a{8})/206265;
    NP=str2double(a{9})/206265;
    TF=str2double(a{10})/206265;
    FF=str2double(a{11})/206265;
    DF=str2double(a{12})/206265;
    if any(isnan([Mra Mde Nstep IH ID CH MA ME NP TF FF DF]))
       uiwait(errordlg('Virhe konfiguraatiotiedoissa!','Konfiguraatio','modal'));
    else okay=1; end;
  end;   
end;
if ~okay
   Mra=Mrai; Mde=Mdei; Nstep=Nstepi; IH=IHi; ID=IDi; CH=CHi; MA=MAi; ME=MEi; NP=NPi; TF=TFi; FF=FFi; DF=DFi;
end;


