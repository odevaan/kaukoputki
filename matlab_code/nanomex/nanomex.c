/*

Mex-version of NANOB interface program for Matlab.

[val,res] = nanomex(COM,flag,addr,val,bit)

Input:
  COM (char) = COM port (COM1,COM2,...)
  flag (char):
        g = get register 
        s = set register 
        h = get flag 
        t = set flag 
        i = get input 
        o = set output 
        r = read bit 
        w = write bit NOT IMPLEMENTED in JET32.DLL 
        x = check JET32.DLL version 
  addr (double) = memory, flag or I/O address
  val (double) = value to set (arbitrary for reading)
  bit (double) = bit number (arbitrary if not needed)

Output:
  val (double) = read or written value
  res (double) = result of operation, 0 if OK
	  
University of Joensuu, Department of Physics

Original code: Jari Räsänen, 2000
MEX code port: Pertti Pääkkönen, 2001

*/

#include "mex.h"
#include <windows.h>
#include <stdio.h>
#include "Jet32test.h"

HJET32 hInterface;

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {

  BOOL JetResult;
  char Flag, ComPort[5], errmsg[40], st[10];
  LONG *InVal, *OutVal;
  double *retval,*retres,*MAddr,*MVal,*MBit;
  WORD *BitNumber;
  DWORD *Address, LastError;
  long DLLVer, NAddr, NVal, NBit, NRes, n;
  char IAddr, IVal, IBit;

  //tarkistetaan parametrien määrä
  if (nrhs < 5)
    mexErrMsgTxt("Required input arguments: COM,flag,addr,val,bit");
  if (!mxIsChar(prhs[0]) || !mxIsChar(prhs[1]))
    mexErrMsgTxt("COM and flag parameters must be of type char");
  if (!mxIsNumeric(prhs[2]) || !mxIsNumeric(prhs[3]) || !mxIsNumeric(prhs[4]))
    mexErrMsgTxt("addr,val, and bit parameters must be numeric");
  for (n=0; n<5; n++)
    if (mxIsEmpty(prhs[n]))
      mexErrMsgTxt("Panic! Empty input array detected! Trying to terminate...");
  if (nlhs > 2) 
    mexErrMsgTxt("Optional output arguments: val,res");

  NAddr=mxGetM(prhs[2])*mxGetN(prhs[2]);
  NVal=mxGetM(prhs[3])*mxGetN(prhs[3]);
  NBit=mxGetM(prhs[4])*mxGetN(prhs[4]);
  NRes=(NAddr>NVal) ? NAddr : NVal;
  NRes=(NRes>NBit) ? NRes : NBit;
  IAddr=(NAddr==NRes);
  IVal=(NVal==NRes);
  IBit=(NBit==NRes);

  Address=calloc(1,sizeof(Address));
  InVal=calloc(1,sizeof(InVal));
  OutVal=calloc(1,sizeof(OutVal));
  BitNumber=calloc(1,sizeof(BitNumber));
  MAddr=mxGetPr(prhs[2]);
  MVal=mxGetPr(prhs[3]);
  MBit=mxGetPr(prhs[4]);

  //rakennetaan vasemman käden parametrit
  if (nlhs>0) {
	  plhs[0]=mxCreateDoubleMatrix(NRes,1,mxREAL);
	  retval=mxGetPr(plhs[0]);
  } else retval=mxCalloc(NRes,sizeof(double));
  if (nlhs>1) {
	  plhs[1]=mxCreateDoubleMatrix(NRes,1,mxREAL);
	  retres=mxGetPr(plhs[1]);
  } else retres=mxCalloc(NRes,sizeof(double));
    
  mxGetString(prhs[0],ComPort,5);
  mxGetString(prhs[1],st,2);
  Flag=st[0];
  
  //printataan dll-versio
  if (tolower(Flag) == 'x') {
  	 DLLVer = Jet32GetDllVersion();
	 /*MajorDLL = LOWORD*/
	 /*MinorDLL = HIWORD*/
	 mexPrintf("Major DLL versio = %d\nMinor DLL version = %d\n", 255 & DLLVer, DLLVer/256);
         mexPrintf("ComPort = %s\n",ComPort);
	 *retres=0;
  } else {
    
    // avataan NANOB-yhteys
    JetResult=Jet32Connect(ComPort,JET32_CT_NANOB,NULL,&hInterface,NULL);

    if (JetResult==0) {
      //Ohjausyksikkoon ei saada yhteytta
      LastError = Jet32GetLastError();
      sprintf(errmsg,"No connection: %i",LastError);
      mexWarnMsgTxt(errmsg);
      for (n=0; n<NRes; n++) retval[n]=retres[n]=-1;
    }
    for (n=0; (n<NRes) && (JetResult!=0); n++) {
      *Address=*MAddr;
      *InVal=*MVal;
      *BitNumber=*MBit;
      *retval=-1;
      *retres=-1;       
      switch (tolower(Flag)) {
        case 'g': //get register
          JetResult=Jet32GetRegister(hInterface,*Address,OutVal);
          if (JetResult==0) {
	         //Toiminto ei onnistunut	
	         LastError = Jet32GetLastError();
            sprintf(errmsg,"Get register error: %i",LastError);
	         mexErrMsgTxt(errmsg);	
          } else {
	         *retval=*OutVal;
	         *retres=0;
          }
	     break;
        case 's': //set register
          JetResult = Jet32SetRegister(hInterface,*Address,*InVal);
	       if (JetResult==0) {
	         //Toiminto ei onnistunut
	         LastError = Jet32GetLastError();
            sprintf(errmsg,"Set register error: %d",LastError);
	         mexErrMsgTxt(errmsg);	
	       } else {
            *retval=*InVal;
	         *retres=0;
          }
	     break;
        case 'i': //get input
           JetResult=Jet32GetBool(hInterface,JET32_BT_IN,*Address,OutVal,0);
           if (JetResult==0) {
	          //Toiminto ei onnistunut
	          LastError = Jet32GetLastError();
	          sprintf(errmsg,"Get input error: %d",LastError);
	          mexErrMsgTxt(errmsg);	
	        } else {
	          *retval=*OutVal;
	          *retres=0;
           }
        break;
        case 'o': //set output
           JetResult=Jet32SetBool(hInterface,JET32_BT_OUT,*Address,*InVal);
            if (JetResult==0) {
             //Toiminto ei onnistunut
             LastError = Jet32GetLastError();
             sprintf(errmsg,"Set output error: %d",LastError);
             mexErrMsgTxt(errmsg);	
	        } else {
	          *retval=*InVal;
	          *retres=0;
           }
        break;
        case 'h': //get flag
	       JetResult=Jet32GetBool(hInterface,JET32_BT_FLAG,*Address,OutVal,0);
	       if (JetResult==0) {
            //Toiminto ei onnistunut
            LastError = Jet32GetLastError();
            sprintf(errmsg,"Get Flag error: %d",LastError);
            mexErrMsgTxt(errmsg);	
          }
	       else {
	         *retval=*OutVal;
	         *retres=0;
          }
        break;
        case 't': //set flag
	       JetResult=Jet32SetBool(hInterface,JET32_BT_FLAG,*Address,*InVal);
	       if (JetResult==0) {
	         //Toiminto ei onnistunut
             LastError = Jet32GetLastError();
             sprintf(errmsg,"Set flag error: %d",LastError);
             mexErrMsgTxt(errmsg);	
	       } else {
	        *retval=*InVal;
	        *retres=0;
          }
        break;
        case 'r': //read bit
	       JetResult=Jet32GetBool(hInterface,JET32_BT_REGBIT,*Address,OutVal,*BitNumber);
	       if (JetResult==0) {
            //Toiminto ei onnistunut
            LastError = Jet32GetLastError();
            sprintf(errmsg,"Bit read error: %d",LastError);
            mexErrMsgTxt(errmsg);	
	       } else {
	         *retval=*OutVal;
	         *retres=0;
          }
        break;
        case 'w'://write bit not implemented in JET32-connection
	       mexErrMsgTxt("Write bit not implemented in JET32 connection");	
        break;
        default:
	       //Toiminto ei onnistunut
	       sprintf(errmsg,"Unknown flag %c",Flag);
	       mexErrMsgTxt(errmsg);
        }
      retval++;
      retres++;
      MAddr+=IAddr;
      MVal+=IVal;
      MBit+=IBit;
    }
  }
}
