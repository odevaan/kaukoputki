function [nous,etel,lask,dawn,dusk]=risetst(nous,etel,lask,dawn,dusk);

if etel<0 etel=['-' dec2hms(etel+24,2)]; 
elseif etel>24 etel=['+' dec2hms(etel-24,2)];
else etel=dec2hms(etel,2); end;
if isinf(nous) | isinf(lask)
   if nous<0
      nous='Näkyy alati';
      lask='Näkyy alati';
   else
      nous='Ei näy';
      lask='Ei näy';
   end;
else
   if nous<0 nous=['-' dec2hms(nous+24,2)]; 
   elseif nous>24 nous=['+' dec2hms(nous-24,2)];
   else nous=dec2hms(nous,2); end;
   if lask<0 lask=['-' dec2hms(lask+24,2)]; 
   elseif lask>24 lask=['+' dec2hms(lask-24,2)];
   else lask=dec2hms(lask,2); end;
end;
if nargout>3
   if isinf(dawn) | isinf(dusk)
      if dawn<0
         dawn='Ei pimene';
         dusk='Ei pimene';
      else
         dawn='Kaamos';
         dusk='Kaamos';
      end;
   else
      if dawn<0 dawn=['-' dec2hms(dawn+24,2)]; 
      elseif dawn>24 dawn=['+' dec2hms(dawn-24,2)];
      else dawn=dec2hms(dawn,2); end;
      if dusk<0 dusk=['-' dec2hms(dusk+24,2)]; 
      elseif dusk>24 dusk=['+' dec2hms(dusk-24,2)];
      else dusk=dec2hms(dusk,2); end;
   end;
end;
