function jd=edbdate(str);
jd=[];
if ~isempty(str)
   date=ones(3,1);
   str=['/' str '/'];
   l=length(str);
   ind=findstr(str,'/');
   dateind=1;
   for j=length(ind):-1:2
      date(dateind)=str2double(str(ind(j-1)+1:ind(j)-1));
      dateind=dateind+1;
   end;
   jd=julian(date(1),date(3),date(2));   
end;
