#ifndef HEADERS_P4
#define HEADERS_P4

#include "defines.p4"

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header ethernet_t {
  macAddr_t dstAddr;
  macAddr_t srcAddr;
  bit<16> etherType;
}

header ipv4_t {
  bit<4> version;
  bit<4> ihl;
  bit<8> diffserv;
  bit<16> totalLen;
  bit<16> identification;
  bit<3> flags;
  bit<13> fragOffset;
  bit<8> ttl;
  bit<8> protocol;
  bit<16> hdrChecksum;
  ip4Addr_t srcAddr;
  ip4Addr_t dstAddr;
}

header nfp_mac_eg_cmd_t {
  bit en_l3_sum;
  bit en_l4_sum;
  bit en_ts_mark;
  bit<29> ignore;
}

header ports_t {
  bit<16> src_port;
  bit<16> dst_port;
}

header intrinsic_metadata_t {
  bit<64> ingress_global_timestamp;
}

struct headers_t {
  nfp_mac_eg_cmd_t nfp_mac_eg_cmd;
  ethernet_t ethernet;
  ipv4_t ipv4;
  ports_t ports;
  intrinsic_metadata_t intrinsic_metadata;
}

struct myParams_t {
  // Fingerprint a ser removida
  bit<32> rm_fingerprint;

  // Fingerprint/position resulting from hash
  bit<32> fingerprint;
  bit<20> index;
}

struct metadata_t {
  bit<20> curr_distinct;
  bit<20> abs;
  bit<20> variation;
  bit<20> current_var;
  bit<20> index;
  bit<1> alarm;
  bit<32> top;
  bit<32> bot;
  myParams_t myParams;
}

struct notification_digest_t {
  bit<20> cur;
  bit<20> absol;
  bit<20> var;
  bit<20> curr_var;
  bit<32> tp;
  bit<32> bt;
}

#endif
