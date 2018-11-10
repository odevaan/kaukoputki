%Mex-version of NANOB interface program for Matlab
%
%[val,res] = nanomex(COM,flag,addr,val,bit)
%
%Input:
%  COM (char) = COM port ('COM1','COM2',...)
%  flag (char):
%        g = get register 
%        s = set register 
%        h = get flag 
%        t = set flag 
%        i = get input 
%        o = set output 
%        r = read bit 
%        w = write bit NOT IMPLEMENTED in JET32.DLL 
%        x = check JET32.DLL version 
%  addr (double) = memory, flag or I/O address
%  val (double) = value to set (arbitrary for reading)
%  bit (double) = bit number (arbitrary if not needed)
%
%Output:
%  val = read or written value
%  res = result of operation, 0 if OK
%	  
%University of Joensuu, Department of Physics
%
%Original code: Jari Räsänen, 2000
%MEX code port: Pertti Pääkkönen, 2001
