function r=isvector(a);

[p,q]=size(a);
r=(p==1 & q>1) | (p>1 & q==1);
