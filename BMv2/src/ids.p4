/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "actions.p4"
#include "checksums.p4"
#include "defines.p4"
#include "parsers.p4"


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

// Circular Fingerprint Buffer (CFB)
register<bit<32>>(550) cfb;

// Frequency Table (FT)
register<bit<20>>(1000) frequency_table;

// Apontador para o mais antigo/próximo a ser substituído
register<bit<20>>(1) first_index;

// Distinct Counter
register<bit<20>>(1) distinct_counter;

// Variation
register<bit<20>>(1) old_distinct_counter;

// Variation
register<bit<20>>(1) variation;

control MyIngress(inout headers_t hdr, inout metadata_t meta,
                  inout standard_metadata_t standard_metadata) {

  // Frequência da fingerprint a ser removida
  bit<20> rm_freq;
  bit<20> prev_rm_freq;

  // Frequência da fingerprint atual
  bit<20> current_freq;

  bit<20> old_distinct;

  // New Variation
  bit<20> current_variation;

  bit<20> diff;
  bit<31> x;
  bit<31> x2;

  bit<1> signal;
  bit<1> abs_signal;

  action process_buffer() {

    // Acquire the position of next element to be replaced
    first_index.read(meta.index, 0);
    
    if(meta.index == 550) {
        meta.index = 0;
    }  
    
    first_index.write(0, meta.index + 1);
    
    distinct_counter.read(meta.curr_distinct, 0);

    // Acquire the fingerprint that is to be removed
    cfb.read(meta.myParams.rm_fingerprint, (bit<32>)meta.index);

    // Writes the new fingerprint in the cyclic buffer
    cfb.write((bit<32>)meta.index, meta.myParams.fingerprint);

  }

  action process_table() {

    // Acquire the frequency of the fingerprint that is to be removed
    frequency_table.read(rm_freq, (bit<32>)meta.myParams.rm_fingerprint);

    // Decrement the frequency of the fingerprint that is to be removed and
    // if it becomes equal to 0, decrement the distinct entry counter
    prev_rm_freq = rm_freq;
    if (rm_freq > 0) {
        rm_freq = rm_freq - 1;
    }

    frequency_table.write((bit<32>)meta.myParams.rm_fingerprint, rm_freq);

    // Acquires the fingerprint frequency at the frequency table
    frequency_table.read(current_freq, (bit<32>)meta.myParams.fingerprint);

    // Increments and updates the frequency of the fingerprint
    current_freq = current_freq + 1;
    frequency_table.write((bit<32>)meta.myParams.fingerprint, current_freq);

    bit<20> decrement_distinct = 0;
    bit<20> increment_distinct = 0;

    if (prev_rm_freq > 0 && rm_freq == 0) {
      decrement_distinct = 1;
    }

    // If it's an entirely new fingerprint within the current cyclic buffer
    // increment the distinct counter
    if (current_freq == 1) {
      increment_distinct = 1;
    }

    // Update the current number of distinct entries
    distinct_counter.write(0, meta.curr_distinct + increment_distinct - decrement_distinct);
  }

  action process_variation() {

    // Old distinct
    old_distinct_counter.read(old_distinct, 0);

    // Update the old distinct counter  
    old_distinct_counter.write(0, meta.curr_distinct);

    // Variation calculation
    variation.read(meta.variation, 0);

    // Absolute value between current and old dictinct counters
    if (meta.curr_distinct > old_distinct) {
        meta.abs = meta.curr_distinct - old_distinct;
        abs_signal = 0;
    } else {
        meta.abs = old_distinct - meta.curr_distinct;
        abs_signal = 1;
    }

    if ((meta.abs * 100) > meta.variation) {
        diff = (meta.abs * 100) - meta.variation;
        signal = 0;
        
        if (abs_signal == 0) {
            meta.alarm = 1;
        }

    } else {
        diff = meta.variation - (meta.abs * 100);
        signal = 1;
    }

    x = ((bit<31>) diff) << 11;
    x2 = (x >> 1) + (x >> 3) + (x >> 4) + (x >> 7) + (x >> 8) + (x >> 11);

    if (signal == 0) {
        current_variation = meta.variation + ((bit<20>) (x2 >> 11));
    } else {
        x2 = x2 > 0 ? (x2 >> 11) + 1 : 0;
        current_variation = meta.variation - (bit<20>) x2;
    }

    meta.current_var = current_variation;

    // Update variation
    variation.write(0, current_variation);

    meta.timestamp = standard_metadata.ingress_global_timestamp;
  }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    table reset_table {
        key = {meta.index : exact;}

        actions = {
        process_variation;
        NoAction;
        }

        default_action = NoAction;

        size = 1;
    }

    action send_notification() {
        digest<notification_digest_t>(1, {meta.curr_distinct, meta.abs, meta.variation, meta.current_var, meta.timestamp});
    }

    apply {

        if (hdr.ipv4.isValid()) {
            
            // Forwards the packet
            ipv4_lpm.apply();
            
            if ((hdr.ports.isValid()) && hdr.ipv4.srcAddr == 167772417) {
                // Generates a fingerprint given the key (DST_IP:DST_PORT)
                compute_hashes(hdr.ipv4.dstAddr ++ hdr.ports.dst_port, meta.myParams.fingerprint);

                process_buffer();

                if (meta.myParams.fingerprint != meta.myParams.rm_fingerprint) {
                    process_table();
                }

                reset_table.apply();

                if (meta.alarm == 1) {
                    send_notification();
                }
            }
        }
    }
}
control MyEgress(inout headers_t hdr, inout metadata_t meta,
                 inout standard_metadata_t standard_metadata) {

apply {
}
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;