/************************************************************
Module name: JET32.H

Notices: 13.02.96  ( by H.Böh out of Oe. )  
			- Version 1.0 

		 19.07.96  ( by H.Böh out of Oe. )
			- Bool-Functions ( IN / OUT / FLAGS )
			- JETWay support
         
         03.02.98 (by cs)
         	- 16Bit support
         	- Jetway-Port1 usable for Multimaster-Modus
************************************************************/

#ifndef __JET32_H__
#define __JET32_H__


#ifdef __cplusplus
extern "C" {
#endif

#ifdef WIN32
	#if !defined(_JET32LIB_)
		#define JET32API __declspec(dllimport) PASCAL
	#else
		#define JET32API __declspec(dllexport) PASCAL
	#endif
#else
	#define JET32API _export CALLBACK
	#define INT int
	#define CHAR char
	#define PCHAR char*
	#define FLOAT float
	#define PFLOAT float*
	#define LPBOOL BOOL FAR *  
	#define MAXBLOCK        80
#endif
	#define LPFLOAT float FAR *

#define JET32_SERIAL_FIRSTPORTNUMBER	1
#define JET32_SERIAL_LASTPORTNUMBER		8

#define JET32_JETWAY_MIN_IOPORT			0x0300
#define JET32_JETWAY_MAX_IOPORT			0x0360 

#define JET32_JETWAY_FIRSTSLAVENUMBER	1
#define JET32_JETWAY_LASTSLAVENUMBER	127

// Connection Strings
#define JET32_SERIAL_IDSTR			"COM"
#define JET32_JETWAY_IDSTR			"JETWay:"
#define JET32_PCPPLC_IDSTR			"PCPPLC:"
// predefined connection strings 	
#define JET32_INTERFACE_SERIAL1		"COM1"
#define JET32_INTERFACE_SERIAL2		"COM2" 
#define JET32_INTERFACE_SERIAL3		"COM3"
#define JET32_INTERFACE_SERIAL4		"COM4" 
#define JET32_INTERFACE_SERIAL5		"COM5"
#define JET32_INTERFACE_SERIAL6		"COM6" 
#define JET32_INTERFACE_SERIAL7		"COM7"
#define JET32_INTERFACE_SERIAL8		"COM8" 
#define JET32_INTERFACE_JETWAY1		"JETWay:1:340"
#define JET32_INTERFACE_JETWAY2		"JETWay:2:340"
#define JET32_INTERFACE_JETWAY3		"JETWay:3:340"
#define JET32_INTERFACE_JETWAY4		"JETWay:4:340"
#define JET32_INTERFACE_JETWAY5		"JETWay:5:340"
#define JET32_INTERFACE_JETWAY6		"JETWay:6:340"
#define JET32_INTERFACE_JETWAY7		"JETWay:7:340"
#define JET32_INTERFACE_JETWAY8		"JETWay:8:340"
#define JET32_INTERFACE_JETWAY9		"JETWay:9:340"
#define JET32_INTERFACE_PCPPLC		"PCPPLC:220:340"		// PPLC on board unit!!!
#define JET32_INTERFACE_PCPPLC_SLV2	"PCPPLC:2:340"			// Slave 2 over PCPPLC board unit!
#define JET32_INTERFACE_PCPPLC_SLV3	"PCPPLC:3:340"			// Slave 3 over PCPPLC board unit!
#define JET32_INTERFACE_PCPPLC_SLV4	"PCPPLC:4:340"			// Slave 4 over PCPPLC board unit!
#define JET32_INTERFACE_PCPPLC_SLV5	"PCPPLC:5:340"			// Slave 5 over PCPPLC board unit!

// JET32 valid baudrates
#define JET32_BAUD9600		9600L
#define JET32_BAUD19200		19200L		// also possible with JETWay
#define JET32_BAUD38400		38400L

#define JET32_BAUD115200	115200		// only JETWay (default)

// JET32 timeout range
#define JET32_MIN_TIMEOUT				100
#define JET32_MAX_TIMEOUT				5000
#define JET32_SERIAL_DEFAULT_TIMEOUT	4000
#define JET32_JETWAY_DEFAULT_TIMEOUT    250

// structure for optional parameters used by Jet32Connect
// zero members will be ignored
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

// Controller Types
#define JET32_CT_PASEE		0
#define JET32_CT_MIKRO		1
#define JET32_CT_DELTA		2
#define JET32_CT_NANOA		3
#define JET32_CT_NANOB		4
#define JET32_CT_NANOC		5
#define JET32_CT_PCPPLC		6
#define JET32_CT_ANY        254
#define JET32_CT_UNKNOWN	255

// Boolean types
#define JET32_BT_IN			0
#define JET32_BT_OUT		1
#define JET32_BT_FLAG		2
#define JET32_BT_REGBIT		3

#define JET32_MAX_REGBIT	31

// 17.12.97: Jet32Command
#define JET32_CMD_START_RAM			'N'
#define JET32_CMD_STOP_AUTOMATIC	'P'
#define JET32_CMD_CONTINUE			'O'

// JET32 error base number
#define MS_USERERROR	0x20000000
#define JET32_ERR_BASE	MS_USERERROR + 0x00001000

// ERROR-Codes called by GetLastError()
#define JET32_ERR_ILLEGAL_INTERFACESTRING		JET32_ERR_BASE + 1
#define JET32_ERR_ILLEGAL_CONTROLLERTYPE		JET32_ERR_BASE + 2
#define JET32_ERR_ILLEGAL_BAUDRATE				JET32_ERR_BASE + 3
#define JET32_ERR_ILLEGAL_TIMEOUT				JET32_ERR_BASE + 4
#define JET32_ERR_CANNOT_DETECT_CONTROLLER		JET32_ERR_BASE + 5
#define JET32_ERR_DIFFERENT_CONTROLLER_IN_USE	JET32_ERR_BASE + 6

#define JET32_ERR_SERIAL_PORT_NOT_AVAILABLE		JET32_ERR_BASE + 11
#define JET32_ERR_SERIAL_ILLEGAL_PORTNUMBER		JET32_ERR_BASE + 12
#define JET32_ERR_SERIAL_CONTROLLER_OFFLINE		JET32_ERR_BASE + 13
#define JET32_ERR_SERIAL_CLIENT_UNDERFLOW		JET32_ERR_BASE + 14

#define JET32_ERR_JETWAY_ILLEGAL_IOPORT			JET32_ERR_BASE + 21
#define JET32_ERR_JETWAY_BOARD_NOT_FOUND		JET32_ERR_BASE + 22
#define JET32_ERR_JETWAY_ILLEGAL_SLAVENUMBER	JET32_ERR_BASE + 23
#define JET32_ERR_JETWAY_CONTROLLER_OFFLINE		JET32_ERR_BASE + 24
#define JET32_ERR_JETWAY_NORESPONSE				JET32_ERR_BASE + 25
#define JET32_ERR_JETWAY_CANNOT_OPEN_DEVICE		JET32_ERR_BASE + 26		// only NT
#define JET32_ERR_JETWAY_DEVICEDRIVER_NOT_FOUND	JET32_ERR_BASE + 27		// only NT

#define JET32_ERR_ILLEGAL_HANDLE				JET32_ERR_BASE + 31
#define JET32_ERR_ILLEGAL_BOOLTYPE				JET32_ERR_BASE + 32
#define JET32_ERR_ILLEGAL_REGBLOCKSIZE			JET32_ERR_BASE + 33
#define JET32_ERR_ILLEGAL_REGBLOCKMODE			JET32_ERR_BASE + 34
#define JET32_ERR_ILLEGAL_REGISTERBIT			JET32_ERR_BASE + 35
#define JET32_ERR_ILLEGAL_POINTER				JET32_ERR_BASE + 36
#define JET32_ERR_ILLEGAL_COMMAND				JET32_ERR_BASE + 37

#define JET32_ERR_VALUE_NOT_WRITTEN				JET32_ERR_BASE + 41 

#define JET32_ERR_PCPPLC_ILLEGAL_IOPORT			JET32_ERR_BASE + 51
#define JET32_ERR_PCPPLC_BOARD_NOT_FOUND		JET32_ERR_BASE + 52
#define JET32_ERR_PCPPLC_ILLEGAL_SLAVENUMBER	JET32_ERR_BASE + 53
#define JET32_ERR_PCPPLC_CONTROLLER_OFFLINE		JET32_ERR_BASE + 54
#define JET32_ERR_PCPPLC_NORESPONSE				JET32_ERR_BASE + 55
#define JET32_ERR_PCPPLC_CANNOT_OPEN_DEVICE		JET32_ERR_BASE + 56		// only NT
#define JET32_ERR_PCPPLC_DEVICEDRIVER_NOT_FOUND	JET32_ERR_BASE + 57		// only NT



#define MAX_REGBLOCKSIZE					32767
// BlockMode Constants
#define JET32_BLOCKMODE_SINLEREGISTER		0
#define JET32_BLOCKMODE_REGINCREMENT		1


/*//////////////////////// JET32 API Functions //////////////////////////////
#ifdef WIN32
	VOID JET32"API JET32GetProc( LPLONG lplJetter);
	VOID JET32"API JET32SetProc( LPLONG lplJetter);
	VOID JET32"API JET32ResetProc( LPLONG lplJetter);
#endif	
*/














/*
Jet32GetDllVersion:

	Return Value: 
		LOWORD = Major DLL version
		HIWORD = Minor DLL version

*/
LONG JET32API 
Jet32GetDllVersion( VOID );


/*
Jet32GetLastError:

	Return Value: 
		Error number of the last function call

*/
DWORD JET32API 
Jet32GetLastError( VOID );


/*
Jet32Connect:

	Parameters:
		lpszInterface
			A null-terminated string like 
			"COM1" 
			or 
			"JETWay:2:340" ( 2..127            = Slavenumber
			                 310, 320, ... 360 = JETWay-IOPort )

		idController
			Use the JET32_CT_xxxx constants

		lpParams
			NULL for this version

		lphInterface
			Interface handle needed by all other JET32 calls

		lpResult
			Not supported in this version

	Return Value: 
		TRUE  = connection successfull
		FALSE = connection error 
				more details by GetLastError ( use JET32_ERR_xxxx constants )

*/
BOOL JET32API
Jet32Connect(
			LPCSTR   lpszInterface,
			INT      idController,
			LPCONNECTPARAM  lpParams,
			LPHJET32 lphInterface,
			LPCONNECTINFO   lpResult
			);


/*
Jet32Disconnect:

Call this function, when a connection to the controller is no more 
used by your program.

	Parameters:
		hInterface
			The handle received by Jet32Connect

	Return Value: 
		TRUE  = disconnection is o.k.
		FALSE = illegal handle

*/
BOOL JET32API
Jet32Disconnect( HJET32 hInterface );


/*
Jet32ConnectStatus:

Call this function, when a Jet32GetXXX or a Jet32SetXXX function
returned FALSE, to be sure that the handle hInterface is still valid.
If a controller is offline, the Jet32.dll makes the handle invalid.
Then you must call Jet32Connect again to get a new handle 

	Parameters:
		hInterface
			The handle received by Jet32Connect

	Return Value: 
		TRUE  = connection is o.k.
		FALSE = invalid handle when a timeout occured

*/
BOOL JET32API
Jet32ConnectStatus( HJET32 hInterface );


BOOL JET32API
Jet32IsFloatRegister( INT idController, DWORD dwRegisterNumber );


BOOL JET32API
Jet32GetRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
 			LPLONG   lplRegisterValue 
			);

BOOL JET32API
Jet32GetRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPLONG   lplRegisterValues 
			);

BOOL JET32API
Jet32GetFloatRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			LPFLOAT  lpflRegisterValue 
			);

BOOL JET32API
Jet32GetFloatRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPFLOAT   lpflRegisterValues 
			);

BOOL JET32API
Jet32GetBool( 
			HJET32   hInterface,
			INT      idBoolType,
			DWORD    dwBoolNumber,
			LPBOOL   lpbBoolValue,
			WORD     nRegisterBit// = 0
			);
	
BOOL JET32API
Jet32GetString( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			WORD     wFlags,
			LPSTR    lpszTextVar
			);



BOOL JET32API
Jet32SetRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			LONG     lRegisterValue 
			);

BOOL JET32API
Jet32SetRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPLONG   lplRegisterValues 
			);

BOOL JET32API
Jet32SetFloatRegister( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			FLOAT    flRegisterValue 
			);

BOOL JET32API
Jet32SetFloatRegisterBlock( 
			HJET32   hInterface,
			INT      nNumber,
			INT      idBlockMode,
			DWORD    dwRegisterNumber, 
			LPFLOAT  lpflRegisterValues 
			);

BOOL JET32API
Jet32SetBool( 
			HJET32   hInterface,
			INT      idBoolType,
			DWORD    dwBoolNumber,
			BOOL     bBoolValue 
			);
	
BOOL JET32API
Jet32SetString( 
			HJET32   hInterface,
			DWORD    dwRegisterNumber, 
			WORD     wFlags,
			LPCSTR   lpszTextVar
			);

BOOL JET32API
Jet32Command( 
			HJET32   hInterface,
			CHAR     idCommand 
			);
	
	

#ifdef __cplusplus
}
#endif


#endif  // __JET32_H__

//////////////////////// End Of JET32.H ////////////////////////
