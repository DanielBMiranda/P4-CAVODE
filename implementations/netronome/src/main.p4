/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "actions.p4"
#include "checksums.p4"
#include "defines.p4"
#include "parsers.p4"

// Circular Fingerprint Buffer (CFB)
register<bit<32>>(550) cfb;

// Frequency Table (FT)
register<bit<20>>(1000) frequency_table;

// Oldest element/next element to be replaced
register<bit<20>>(1) first_index;

// Distinct Counter
register<bit<20>>(1) distinct_counter;

// Variation
register<bit<20>>(1) old_distinct_counter;

// Variation
register<bit<20>>(1) variation;

/**
* These pragamas ensure mutual exclusion when accessing a register.
* NOTE: As of the latest SDK version, the Netronome compiler ignores these pragmas when using P4_16.
*/

#pragma netro reglocked cfb;
#pragma netro reglocked frequency_table;
#pragma netro reglocked first_index;
#pragma netro reglocked distinct_counter;
#pragma netro reglocked old_distinct_counter;
#pragma netro reglocked variation;

/**
* Calls the spin-locks associated with each structure.
*/
extern void cep_index_lock();
extern void cep_index_unlock();

extern void cep_distinct_lock();
extern void cep_distinct_unlock();

extern void cep_old_distinct_lock();
extern void cep_old_distinct_unlock();

extern void cep_cfb_lock();
extern void cep_cfb_unlock();

extern void cep_variation_lock();
extern void cep_variation_unlock();

extern void cep_position_lock();
extern void cep_position_unlock();

extern void cep_rm_position_lock();
extern void cep_rm_position_unlock();

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers_t hdr, inout metadata_t meta,
                  inout standard_metadata_t standard_metadata) {

  // Frequency of the fingerprint to be removed
  bit<20> rm_freq;
  bit<20> prev_rm_freq;

  // Current fingerprint frequency
  bit<20> current_freq;

  // Previous distinct counter value
  bit<20> old_distinct;

  // Current distinct counter value
  bit<20> current_distinct;

  // New Variation
  bit<20> current_variation;

  // Auxiliary variables for calculating Variation
  bit<20> diff;
  bit<31> x;
  bit<31> x2;
  bit<1> signal;
  bit<1> abs_signal;

  /**
   * Updates the buffer with the current fingerprint and increments its index.  
   * Resets the buffer when a cycle is completed.  
   * Additionaly, it stores the current distinct count as metadata, which is later used for variation calculations  when a cycle is completed.    
   **/

  action process_buffer() {

    cep_index_lock();

        // Acquire the position of next element to be replaced
        first_index.read(meta.index, 0);
        
        // If a rotation was completed, reset the index
        if(meta.index == 550) {
          meta.index = 0;
        }  
        
        // Update the index register
        first_index.write(0, meta.index + 1);
        
        // Acquire the current distinct count
        distinct_counter.read(meta.curr_distinct, 0);
        
    cep_index_unlock();

    // Add 11000 to the index to associate with its spin-lock
    meta.myParams.index = meta.index + 11000;

    cep_cfb_lock();
    
        // Acquire the fingerprint that is to be removed
        cfb.read(meta.myParams.rm_fingerprint, (bit<32>)meta.index);

        // Writes the new fingerprint in the cyclic buffer
        cfb.write((bit<32>)meta.index, meta.myParams.fingerprint);

    cep_cfb_unlock();
  }

  /**
   * Updates the buffer with the current fingerprint and increments its index.  
   * Resets the buffer when a cycle is completed.  
   * Additionaly, it stores the current distinct count as metadata, which is later used for variation calculations when a cycle is completed.    
   **/

  action process_table() {

    cep_rm_position_lock();

        // Acquire the frequency of the fingerprint that is to be removed
        frequency_table.read(rm_freq, (bit<32>)meta.myParams.rm_fingerprint);

        // Decrement the frequency of the fingerprint that is to be removed and
        // if it becomes equal to 0, decrement the distinct entry counter
        prev_rm_freq = rm_freq;
        if (rm_freq > 0) {
          rm_freq = rm_freq - 1;
        }

        // Update the frequency at the frequency table
        frequency_table.write((bit<32>)meta.myParams.rm_fingerprint, rm_freq);

    cep_rm_position_unlock();

    cep_position_lock();

        // Acquires the fingerprint frequency at the frequency table
        frequency_table.read(current_freq, (bit<32>)meta.myParams.fingerprint);

        // Increments and updates the frequency of the fingerprint
        current_freq = current_freq + 1;
        frequency_table.write((bit<32>)meta.myParams.fingerprint, current_freq);

    cep_position_unlock();

    bit<20> decrement_distinct = 0;
    bit<20> increment_distinct = 0;

    // If an element's frequency reaches 0, it hasn't yet appeared in the cycle, so the distinct counter is decremented.
    if (prev_rm_freq > 0 && rm_freq == 0) {
      decrement_distinct = 1;
    }

    // If it's an entirely new fingerprint within the current cyclic buffer increment the distinct counter
    if (current_freq == 1) {
      increment_distinct = 1;
    }

    cep_distinct_lock();

        // Check number of distinct elements
        distinct_counter.read(current_distinct, 0);

        // Update the current number of distinct entries
        distinct_counter.write(0, current_distinct + increment_distinct - decrement_distinct);

    cep_distinct_unlock();
  }

  /**
   * Updates the buffer with the current fingerprint and increments its index.  
   * Resets the buffer when a cycle is completed.  
   * Additionaly, it stores the current distinct count as metadata, which is later used for variation calculations when a cycle is completed.    
   **/

  action process_variation() {

    cep_old_distinct_lock();
        // Old distinct
        old_distinct_counter.read(old_distinct, 0);

        // Update the old distinct counter  
        old_distinct_counter.write(0, meta.curr_distinct);
    cep_old_distinct_unlock();

    cep_variation_lock();

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

    cep_variation_unlock();

    // Split the timestamp: the upper part represents seconds, and the lower part represents nanoseconds.
    meta.top = hdr.intrinsic_metadata.ingress_global_timestamp[63:32];
    meta.bot = hdr.intrinsic_metadata.ingress_global_timestamp[31:0];
  }

  #pragma netro no_lookup_caching process_buffer
  #pragma netro no_lookup_caching process_table
  #pragma netro no_lookup_caching process_variation


  action update_egress(bit<16> port) { standard_metadata.egress_spec = port; }

  table table_vf_forward {
    key = {standard_metadata.ingress_port : exact;}

    actions = {update_egress;}

    size = 4;
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

apply {
  table_vf_forward.apply();
  if ((hdr.ports.isValid()) && standard_metadata.ingress_port == 0x000 && hdr.ipv4.srcAddr == 167772161) {
    
    // Generates a fingerprint given the key (DST_IP:DST_PORT)
    compute_hashes(hdr.ipv4.dstAddr ++ hdr.ports.dst_port, meta.myParams.fingerprint);

    // Processes the cyclic buffer related operations
    process_buffer();

    // If the current fingerprint differs from the previous one, process the frequency table operations
    if (meta.myParams.fingerprint != meta.myParams.rm_fingerprint) {
      process_table();
    }

    // If a reset has ocurred then apply the variation calculation
    reset_table.apply();
  }
}
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers_t hdr, inout metadata_t meta,
                 inout standard_metadata_t standard_metadata) {

  // action nop() {}
  action add_empty_nfp_mac_eg_cmd() {
    hdr.nfp_mac_eg_cmd.setValid();
    hdr.nfp_mac_eg_cmd = {0, 1, 0, 0x0};
  }

  // Allows a notification to be sent using the stored metadata
  action send_notification() {
    digest<notification_digest_t>(1, {meta.curr_distinct, meta.abs, meta.variation, meta.current_var, meta.top, meta.bot});
  }

  table table_add_empty_nfp_mac_eg_cmd {
    key = {standard_metadata.egress_port : exact;}

    actions = {
      NoAction;
      add_empty_nfp_mac_eg_cmd;
    }
    default_action = NoAction;
    size = 2;
  }

  table notification_table {
    key = {meta.alarm : exact;}

    actions = {
      send_notification;
      NoAction;
    }

    default_action = NoAction;

    size = 1;
  }

apply {
  table_add_empty_nfp_mac_eg_cmd.apply();

  // If an alarm has occured a notification is sent with the appropriate metadata
  notification_table.apply();
}
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(),
         MyComputeChecksum(), MyDeparser()) main;