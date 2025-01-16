#ifndef __DEFINES__
#define __DEFINES__

/*************************************************************************
*********************** D E F I N E S ************************************
*************************************************************************/

/**
 * These constants define protocol-specific identifiers for use in the parser's transitions.
 **/

#define TYPE_IPV4 0x0800
#define TYPE_TCP 8w6
#define TYPE_UDP 8w17

/**
 * These typedefs define common bit-width types for specific fields in network protocols.
 **/

typedef bit<16> egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

#endif
