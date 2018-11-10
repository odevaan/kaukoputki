//#define  int
#define INT int
#define CHAR char
#define PCHAR char*
#define FLOAT float
#define PFLOAT float*
#define LPFLOAT float*
#define LPBOOL BOOL FAR *  
#define LPCSTR char*

typedef struct tagCONNECTPARAM {
	DWORD dwSize;				// structure size
	DWORD dwBaudrate;
	WORD  wTimeout;      
	BOOL  bForceOldProtocol;	// for PASEE (if necessary) and MIKRO
} CONNECTPARAM, *PCONNECTPARAM, FAR *LPCONNECTPARAM;

#define CONNECTPARAMSIZE	(DWORD)sizeof(CONNECTPARAM)	

typedef struct tagCONNECTINFO {
	DWORD dwSize;				// structure size
	BOOL  bSizeError;		
	int   idController;
	// LOBYTE = major version number
	// HIBYTE = minor version number
	WORD  wControllerVersion;			
	DWORD dwBaudrate;
	WORD  wTimeout;      
	BOOL  bOldProtocolForced;	
} CONNECTINFO, *PCONNECTINFO, FAR *LPCONNECTINFO;

#define CONNECTINFOSIZE		(DWORD)sizeof(CONNECTINFO)	

// JET32 handle type
typedef LONG    HJET32;
typedef LPLONG  LPHJET32;

#define JET32_CT_NANOB		4
#define JET32_BT_IN			0
#define JET32_BT_OUT		1
#define JET32_BT_FLAG		2
#define JET32_BT_REGBIT		3


LONG  
Jet32GetDllVersion( VOID ) {
  return(65535);   
}


DWORD  
Jet32GetLastError( VOID ) {
  return(100);   
}


BOOL 
Jet32Connect(
			LPCSTR   lpszInterface,
			INT      idController,
			LPCONNECTPARAM  lpParams,
			LPHJET32 lphInterface,
			LPCONNECTINFO   lpResult
         ) {
  return(1);         
}


BOOL 
Jet32Disconnect( HJET32 hInterface ) {
  return(1);
}


BOOL 
Jet32ConnectStatus( HJET32 hInterface ) {
  return(1);
}


BOOL 
Jet32IsFloatRegister( INT idController, DWORD dwRegisterNumber ) {
  return(1);
};


BOOL 
Jet32GetRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
 			LPLONG   lplRegisterValue 
			) {
  *lplRegisterValue=dwRegisterNumber;
  return(1);
}

BOOL 
Jet32GetRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPLONG   lplRegisterValues 
			) {
  return(1);
}

BOOL 
Jet32GetFloatRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			LPFLOAT  lpflRegisterValue 
			) {
  *lpflRegisterValue=3.14;
  return(1);
}

BOOL 
Jet32GetFloatRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPFLOAT   lpflRegisterValues 
			) {
  return(1);
}

BOOL 
Jet32GetBool( 
			HJET32   hInterface,
			INT      idBoolType,
			DWORD    dwBoolNumber,
			LPBOOL   lpbBoolValue,
			WORD     nRegisterBit// = 0
			) {
  *lpbBoolValue=1;
  return(1);
}
	
BOOL 
Jet32GetString( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			WORD     wFlags,
			LPSTR    lpszTextVar
			) {
  lpszTextVar=0;
  return(1);
};



BOOL 
Jet32SetRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			LONG     lRegisterValue 
			) {
  return(1);
}

BOOL 
Jet32SetRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPLONG   lplRegisterValues 
			) {
  return(1);
}

BOOL 
Jet32SetFloatRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			FLOAT    flRegisterValue 
			) {
  return(1);
}

BOOL 
Jet32SetFloatRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPFLOAT  lpflRegisterValues 
			){
  return(1);
}

BOOL 
Jet32SetBool( 
			HJET32   hInterface,
			INT      idBoolType,
			DWORD    dwBoolNumber,
			BOOL     bBoolValue 
			){
  return(1);
}
	
BOOL 
Jet32SetString( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			WORD     wFlags,
			LPCSTR   lpszTextVar
			){
  return(1);
}

BOOL 
Jet32Command( 
			HJET32   hInterface,
			CHAR     idCommand 
			){
  return(1);
}
