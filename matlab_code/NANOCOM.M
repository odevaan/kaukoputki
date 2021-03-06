function value = nanocom(Type, Address, Value, BitNum)
%function value = nanocom(Type, Address, Value, BitNum)
%
% T�m� funktio on liittym� NanoB-ohjaimeen. Funktiolla 
% voidaan lukea ja kirjoittaa NanoB:n rekistereit�,
% lippuja (flag) ja I/O-portteja.
% Ohjelma k�ytt�� liikenn�intiin joko
%1) konsoliohjelmaa, jonka parametrit saat n�kyviin 
%   kirjoittamalla NANOCOM Windows-komentopromptiin
%tahi
%2) MEX-funktiota nanomex.dll
%
%MEX-funktio valitaan k�ytt��n rivill� 42: "ismex=1;"
%
% Parametrit
% 	type
%		GetReg		lukee rekisterin
%		SetReg		kirjoittaa rekisteriin
%		GetFlag   lukee lipun
%		SetFlag	kirjoittaa lipun
%		GetInput	lukee input-portin
%		SetOutput	asettaa output-portin
%		GetBit		lukee rekisterin bitin
%		SetBit		asettaa rekisterin bitin
%
%	Adress
%		rekisterin yms. osoite
%	
%	Value
%		kirjoitettava arvo (annetaan vain tarvittaessa)
%
%	BitNum
%		bitin numero [0-31]
%
%	Esim:
%		nanocom('getreg',1024)
%		nanocom('setreg',1024,5)
%		nanocom('getbit',1024,0,14)		% luetaan bitti 14. Huom! kolmas parametri pit�� olla
%		nanocom('setbit',1024,1,14)		% asetetaan bitti 14 ykk�seksi

%onko MEX versio?
ismex=1;

%testaamiseen ilman Nano-B:t�
%disp('Testing nanocom.m without connection!'); value=[]; return;

% m��ritet��n k�ytett�v� com-portti
ComPort = 'COM1';

%value=0; warning('Nanocom.m inaktiivinen!'); return; % Testaukseen ilman Nanoa

switch lower(Type)
case 'getreg'
   ctype = 'g'; Value = 0; BitNum = 0;
case 'setreg'
   ctype = 's'; BitNum = 0;
case 'getflag'
   ctype = 'h'; Value = 0; BitNum = 0;
case 'setflag'
   ctype = 't'; BitNum = 0; 
case 'getinput'
   ctype = 'i'; Value = 0; BitNum = 0;
case 'setoutput'
   ctype = 'o'; BitNum = 0; 
case 'getbit'
   ctype = 'r'; Value = 0;
case 'setbit'	
   % setbit operaatioita ei ole implementoitu jet32.dll:ss�, joten tehd��n se t�ss�
	% kutsumalla rekursiivisesti t�t� funktiota
   A = nanocom('getreg', Address); % luetaan rekisterin arvo
   % asetetaan haluttu bitti
   % Huom! Matlabissa LSB m��ritell��n nollaksi ja NanoB:s� ykk�seksi 
   Value = bitset(A,BitNum+1,Value); 
   ctype = 's'; 
otherwise
   disp('Unknown type'); BitNum = 0;
   return
end

if (ismex)
   [value,res]=nanomex(ComPort,ctype,Address,Value,BitNum);
   if any(res~=0)
       disp('Yhteys NanoB-ohjaimeen ei onnistunut!');
       disp('Onhan ohjausyksikk� k�ynnistetty ja sarjaliit�nt� kytketty?');
       disp('Katso tarkempi virheilmoitus komentorivilt�.');
       disp('LastError -koodin merkitys l�ytyy jet32.h tiedostosta');
   end;    
else   
  Address = num2str(Address);
  Value = num2str(Value);
  BitNum = num2str(BitNum);

  if isempty(Value) warning('Empty Value'); end;

  cmdstr = ['nanocom ' ComPort ' ' ctype ' ' Address ' ' Value ' ' BitNum];
  [stat result] = dos(cmdstr);

  if stat 
    disp('Komentoriviohjelman ajaminen ei onnistunut');
    disp(result);
    return
  end

  % tarkistetaan onko palautetussa merkkijonossa muuta kuin numeroita
  if ~isletter(result)
    % kaikki numeroita
	 t = str2num(result);
	 value = t(1);
	 ok = t(2);
	 errorstat = t(3);

 	 if ~ok
      disp('    ');
   	   disp(['Yhteys NanoB-ohjaimeen ei onnistunut (LastError-koodi = 0x' dec2hex(errorstat) ')']);
 	   disp('Onhan ohjausyksikk� k�ynnistetty ja sarjaliit�nt� kytketty');
  	   disp('LastError -koodin merkitys l�ytyy jet32.h tiedostosta');
   	   value = [];
    end
  else 
    % palautteessa my�s muita kuin numeroita
    % palautetaan tyhj� matriisi ja kirjoitetaan n�ytt��n result-muuttujan tulos merkkijonona
    disp('Komentoriviohjelman palautteessa muita merkkej� kuin numeroita');
    disp(['palaute: ' result])
    value = [];
  end
end;

   
