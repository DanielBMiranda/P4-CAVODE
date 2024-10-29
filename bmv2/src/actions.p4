#ifndef __ACTIONS__
#define __ACTIONS__

#include "headers.p4"

/*************************************************************************
*********************** A C T I O N S  ***********************************
*************************************************************************/

action compute_hashes(in bit<48> full_key, out bit<32> pos) {
  hash(pos, HashAlgorithm.crc32, (bit<32>)0, {full_key}, (bit<32>)1000);
}

#endif