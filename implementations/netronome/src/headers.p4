#ifndef HEADERS_P4
#define HEADERS_P4

#include "defines.p4"

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

/**
 * Describes the Ethernet protocol.
 **/

header ethernet_t {
  macAddr_t dstAddr;
  macAddr_t srcAddr;
  bit<16> etherType;
}

/**
 * Describes the IPv4 protocol.
 **/

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

/**
 * Describes the TCP/UDP source and destination ports.
 **/

header ports_t {
  bit<16> src_port;
  bit<16> dst_port;
}

/**
 * Describes the current timestamp.
 **/

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

/**
 * This structure holds parameters related to the locking mechanisms on multiple element registers.
 * Each parameter is associated with a different lock dedicated to a position in a register.
 **/

struct myParams_t {
  bit<32> rm_fingerprint; // Fingerprint to be removed
  bit<32> fingerprint;  // Fingerprint/position resulting from hash
  bit<20> index;  // Current cyclic buffer index
}

/**
 * This structure represents metadata used between different processing blocks in the pipeline. 
 **/

struct metadata_t {
  bit<20> curr_distinct;  // Current distinct counter
  bit<20> abs;  // Difference between previous and current distinct counters
  bit<20> variation;  // Previous variation
  bit<20> current_var;  // New variation
  bit<20> index;  // Current cyclic buffer index
  bit<1> alarm; // Bit that indicates if an alarm has occurred
  bit<32> top; // Top part of the timestamp (seconds)
  bit<32> bot; // Bottom part of the timestamp (nanoseconds)
  myParams_t myParams;
}

/**
 * Describes the parameters sent when an alarm is triggered.
 **/

struct notification_digest_t {
  bit<20> cur;  // Current distinct counter
  bit<20> absol;  // Difference between previous and current distinct counters
  bit<20> var;  // Previous variation
  bit<20> curr_var; // New variation
  bit<32> tp; // Top part of the timestamp (seconds)
  bit<32> bt; // Bottom part of the timestamp (nanoseconds)
}

#endif
