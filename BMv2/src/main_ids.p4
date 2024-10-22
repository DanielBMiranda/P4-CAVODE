/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "defines.p4"
#include "parsers.p4"
#include "checksums.p4"
#include "actions.p4"

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    
    // Table
    register<bit<6>>(1000) distinct_table;

    bit<32> position;

    // Last window of an entry
    bit<6> last_table_window;

    // Distinct Counter
    register<bit<30>>(1) distinct_counter;

    // Current distinct counter value
    bit<30> current_distinct;

    // Observation window counter
    register<bit<6>>(1) ow_counter;

    // Current observation window
    bit<6> current_wid;

    // Timestamp reset
    register<bit<TIMESTAMP_SIZE>>(1) reset;

    // Last timestamp reset
    bit<TIMESTAMP_SIZE> reset_ts;

    // EWMA
    register<bit<30>>(1) ewma;

    // New EWMA
    bit<30> old_ewma;

    // New EWMA
    bit<30> current_ewma;

    int<30> diff;

    int<41> x;
    int<41> x2;

    // Time
    bit<48> current_ts;

    // Scan ocurrence
    register<bit<2>>(1) scan_ocurred;
    bit<2> scan_ocurrence;

    // scan detected
    register<bit<2>>(1) scan_detected;
    bit<2> scan;

    action compute_hashes(in bit<16> port, out bit<32> pos) {
        hash(pos, HashAlgorithm.crc32, (bit<32>) 0, {port}, (bit<32>) 1000);
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

    apply {
        
        // Obter o identificador da janela de tempo atual
        ow_counter.read(current_wid, 0);

        if (current_wid == 0) {
            ow_counter.write(0, 1);
            ewma.write(0, EWMA_0);
        }
        
        // Obter a timestamp do último reset
        reset.read(reset_ts, 0);
        
        current_ts = standard_metadata.ingress_global_timestamp;

        // Se já tiver-se passado o tempo da time window atual
        if(current_ts - reset_ts > RESET_T) {

            ow_counter.read(current_wid, 0);

            // Se o número limite de janelas tiver sido alcançado reseta-se
            if(current_wid == 30) {
                ow_counter.write(0, 1);

            } else { // Senão incrementa-se a janela temporal e atualiza-se no register
                ow_counter.write(0, current_wid + 1);
            }

            // EWMA calculation
            ewma.read(old_ewma, 0);
            distinct_counter.read(current_distinct, 0);

            diff = ((int<30>) (current_distinct * 10000)) - ((int<30>) old_ewma);

            x = ((int<41>) diff) << 11;

            x2 = (x >> 1) + (x >> 2) + (x >> 3) + (x >> 6) + (x >> 7) + (x >> 10) + (x >> 11);

            current_ewma = old_ewma + ((bit<30>) ((int<30>) (x2 >> 11)));
            
            scan_ocurred.read(scan_ocurrence, 0);

            //send_notification(2 + scan_ocurrence, current_distinct, current_ewma);
            if(current_ewma > 30000) {
                scan_detected.write(0, 2);
                ewma.write(0, old_ewma);
            } else {
                ewma.write(0, current_ewma);
            }

            scan_detected.read(scan, 0);

            send_notification(scan + scan_ocurrence, current_distinct, current_ewma);
            
            scan_detected.write(0, 0);

            scan_ocurred.write(0, 0);

            // atualiza-se a timestamp do último reset e reseta-se o contador
            reset.write(0, current_ts);
            distinct_counter.write(0, 0);
        }

        if (hdr.ipv4.isValid()) {
            
            ipv4_lpm.apply();
            
            // Se for pacote TCP
            if(hdr.tcp.isValid() || hdr.udp.isValid()) {
                
                compute_hashes(meta.dest_port, position);
                // ver a ultima janela de observaçao desta entrada e o número de distintos
                distinct_table.read(last_table_window, position);
                ow_counter.read(current_wid, 0);

                // Se a última janela da entrada for diferente da atual
                if(last_table_window != current_wid) {
                    distinct_counter.read(current_distinct, 0);
                    distinct_counter.write(0, current_distinct + 1);
                    distinct_table.write(position, current_wid);
                }

                if (hdr.ipv4.srcAddr == 3232294600) {
                    scan_ocurred.write(0, 1);
                }
                
            }
        }
    }
}
/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
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