function makeplanetf(p,name);

load vsop87;
f=fopen([name '.m'],'w');
fprintf(f,'function [L,B,R]=%s(jde);\n',name);
fprintf(f,'N=length(jde(:));\n');
fprintf(f,'t=ones(6,1)*(jde(:)''-2451545)/365250; t(1,:)=1;\n');
fprintf(f,'t=cumprod(t);\n');
fprintf(f,'L=zeros(1,N); B=L; R=L;\n');

nVL=0; nVB=0; nVR=0;
for v=0:5
  I=squeeze(vsopind(p,1,v+1,:));
  if I(2)>0 
     nVL=v; 
     V=vsopvar(I(1)+(0:I(2)-1),:);
     fprintf(f,'VL%1.0f=[',v);
     for ind=1:length(V(:,1))-1; fprintf(f,'%1.14g,%1.14g,%1.14g\n',V(ind,:)); end;
     fprintf(f,'%1.14g,%1.14g,%1.14g];\n',V(end,:));
  end;
end;
for v=0:5
  I=squeeze(vsopind(p,2,v+1,:));
  if I(2)>0 
     nVB=v; 
     V=vsopvar(I(1)+(0:I(2)-1),:);
     fprintf(f,'VB%1.0f=[',v);
     for ind=1:length(V(:,1))-1; fprintf(f,'%1.14g,%1.14g,%1.14g\n',V(ind,:)); end;
     fprintf(f,'%1.14g,%1.14g,%1.14g];\n',V(end,:));
  end;
end;
for v=0:5
  I=squeeze(vsopind(p,3,v+1,:));
  if I(2)>0 
     nVR=v; 
     V=vsopvar(I(1)+(0:I(2)-1),:);
     fprintf(f,'VR%1.0f=[',v);
     for ind=1:length(V(:,1))-1; fprintf(f,'%1.14g,%1.14g,%1.14g\n',V(ind,:)); end;
     fprintf(f,'%1.14g,%1.14g,%1.14g];\n',V(end,:));
  end;
end;
for v=0:nVL
   fprintf(f,'L=L+sum(VL%1.0f(:,1)*ones(1,N).*cos(VL%1.0f(:,2)*ones(1,N)+VL%1.0f(:,3)*t(2,:)),1).*t(%1.0f,:);\n',v,v,v,v+1);
end;
fprintf(f,'L=mod2pi(L);\n');
for v=0:nVB
   fprintf(f,'B=B+sum(VB%1.0f(:,1)*ones(1,N).*cos(VB%1.0f(:,2)*ones(1,N)+VB%1.0f(:,3)*t(2,:)),1).*t(%1.0f,:);\n',v,v,v,v+1);
end;
for v=0:nVR
   fprintf(f,'R=R+sum(VR%1.0f(:,1)*ones(1,N).*cos(VR%1.0f(:,2)*ones(1,N)+VR%1.0f(:,3)*t(2,:)),1).*t(%1.0f,:);\n',v,v,v,v+1);
end;

fclose(f);
