#ifndef PARSER_P4
#define PARSER_P4

#include "headers.p4"

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet, out headers_t hdr, inout metadata_t meta,
                inout standard_metadata_t standard_metadata) {

  state start { transition parse_ethernet; }

  state parse_ethernet {
    packet.extract(hdr.ethernet);
    transition select(hdr.ethernet.etherType) {
    TYPE_IPV4:
      parse_ipv4;
    default:
      accept;
    }
  }

  state parse_ipv4 {
    packet.extract(hdr.ipv4);
    transition select(hdr.ipv4.protocol) {
    TYPE_TCP:
      parse_ports;
    TYPE_UDP:
      parse_ports;
    default:
      accept;
    }
  }

  state parse_ports {
    packet.extract(hdr.ports);
    meta.curr_distinct = 0;
    meta.abs = 0;
    meta.variation = 0;
    meta.index = 0;
    meta.alarm = 0;
    meta.top = 0;
    meta.bot = 0;
    meta.current_var = 0;
    transition accept;
  }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers_t hdr) {
  apply { packet.emit(hdr); }
}

#endif
