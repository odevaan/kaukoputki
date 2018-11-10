function name=getedbname(name);

AddOpts.Interpreter='tex'; AddOpts.Resize='off'; AddOpts.WindowStyle='normal';
txt={'Komeetan tai asteroidin nimi'};
name=inputdlg(txt,'XEphem EDB-tietokanta',[1 40],{name},AddOpts);
if isempty(name) name={''}; end;
