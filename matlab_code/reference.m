function refok=reference;

global stopit;

stopit=0;  % Stop-nappulan tila
refok=0;   % referenssi ajettu
if strcmp(questdlg('Onko kaukoputki ekvatoriaalisen tunti- ja deklinaatiokoordinaatiston nollasuunnan itä- ja eteläpuolella?','Varmistus','On','Ei vielä','On'),'On')
   
  %Tämä koodi on pääosin FM Marjut Ristolan pro gradu- työstä v. 2000.
   
  SiirtoV1 = 2000; % Referenssiajon nopeus
  
  % Home-detektorin polaarisuus käännetään alhaalla aktiiviseksi.
  nanocom('SetBit',12104,0,0);     
  nanocom('SetBit',13104,0,0);

  value1 = nanocom('GetReg',12109); % Ennen position controliin   
  nanocom('SetReg',12102,value1);   % siirtymistä nominal rekisterin 
  value2 = nanocom('GetReg',13109); % arvoksi sijoitetaan 
  nanocom('SetReg',13102,value2);   % actual rekisterin arvo.

  %nanocom('SetOutput',101,1);       % Summeri päälle.
  nanocom('SetBit',12100,1,9);      % Position control
  nanocom('SetReg',12103,SiirtoV1); % Asetetaan nopeus.
  nanocom('SetBit',13100,1,9);
  nanocom('SetReg',13103,SiirtoV1);

  %Jos putki on jo kotiasennossa, peruutetaan kunnes optohaarukat vapaat
  value1 = nanocom('GetBit',12100,0,1); % Onko deklinaatioakseli referenssissä?
  if value1
    nanocom('SetReg',12101,9); % deklinaatioakseli positiiviseen suuntaan.
    while value1 & ~stopit
       value1 = nanocom('GetBit',12100,0,1); % Vieläkö ollaan referenssissä?
       pause(0);
    end;
    nanocom('SetReg',12101,10); % deklinaatioakseli negatiiviseen suuntaan.
  end;

  value2 = nanocom('GetBit',13100,0,1); % Onko tuntiakseli referenssissä?
  if value2
    nanocom('SetReg',13101,10);  % tuntiakseli negatiiviseen suuntaan.
    while value2  & ~stopit
       value2 = nanocom('GetBit',13100,0,1); % vieläkö ollaan referenssissä?
       pause(0);
    end;
    nanocom('SetReg',13101,9);  % tuntiakseli positiiviseen suuntaan.
  end;

  %Varsinainen referenssiajo
  while (~value1 | ~value2) & ~stopit  % Etsitään referenssiä.
     if ~value1
       value1 = nanocom('GetBit',12100,0,1); % onko deklinaatioakseli referenssissä?
       if value1
         nanocom('SetBit',12100,0,9);        % takaisin speed-controliin
       end;
     end;
     if ~value2
       value2 = nanocom('GetBit',13100,0,1); % onko tuntiakseli referenssissä?
       if value2
         nanocom('SetBit',13100,0,9);        % takaisin speed-controliin
       end;
     end;
     pause(0);
  end
  nanocom('SetOutput',101,0);     % Summeri pois päältä.   
  refok=(value1 & value2);
  if ~refok                       % Jos ei löytynyt annetaan virheilmoitus.
     nanocom('SetBit',12100,0,9); % takaisin speed-controliin
     nanocom('SetBit',13100,0,9);
     refok=0;
     warndlg('Referenssiä ei löytynyt!','Huom!','modal');
  else
     warndlg('Referenssiajo suoritettu!','Cool!','modal');
  end;
end;
