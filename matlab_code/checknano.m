function nanook=checknano;

nanook=~isempty(nanocom('GetReg',12109));
if ~nanook
   msgbox('Yhteys NanoB- ohjaimeen ei toimi tai on sattunut toimintavirhe. Katso tarkempi virheilmoitus Matlabin komentoriviltä.','NanoB','error','modal');
else
  %Moottoreiden resoluutio: 32 = 512 steppiä/kierros
  %Tehdään position-rekistereiden ylivuodon välttämiseksi
  nanocom('SetReg',12122,32);
  nanocom('SetReg',13122,32);
end;
