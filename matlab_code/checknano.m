function nanook=checknano;

nanook=~isempty(nanocom('GetReg',12109));
if ~nanook
   msgbox('Yhteys NanoB- ohjaimeen ei toimi tai on sattunut toimintavirhe. Katso tarkempi virheilmoitus Matlabin komentorivilt‰.','NanoB','error','modal');
else
  %Moottoreiden resoluutio: 32 = 512 steppi‰/kierros
  %Tehd‰‰n position-rekistereiden ylivuodon v‰ltt‰miseksi
  nanocom('SetReg',12122,32);
  nanocom('SetReg',13122,32);
end;
