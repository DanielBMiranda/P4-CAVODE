#ifndef HEADERS_P4
#define HEADERS_P4

#include "defines.p4"

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header ports_t {
  bit<16> src_port;
  bit<16> dst_port;
}

struct headers_t {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    ports_t ports;
}

struct myParams_t {
  // Fingerprint a ser removida
  bit<32> rm_fingerprint;

  // Fingerprint/position resulting from hash
  bit<32> fingerprint;
}

struct metadata_t {
  bit<20> curr_distinct;
  bit<20> abs;
  bit<20> variation;
  bit<20> current_var;
  bit<20> index;
  bit<1> alarm;
  bit<48> timestamp;
  myParams_t myParams;
}

struct notification_digest_t {
  bit<20> cur;
  bit<20> absol;
  bit<20> var;
  bit<20> curr_var;
  bit<48> ts;
}

#endif