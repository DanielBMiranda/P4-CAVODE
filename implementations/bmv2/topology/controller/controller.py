#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep
import threading
import grpc
import zlib
import datetime

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.switch import ShutdownAllSwitchConnections


def writeTunnelRules(p4info_helper, ingress_sw, egress_sw, tunnel_id,
                     dst_eth_addr, dst_ip_addr, switch_to_host_port, switch_to_switch_port):
    """
    Installs three rules:
    1) An tunnel ingress rule on the ingress switch in the ipv4_lpm table that
       encapsulates traffic into a tunnel with the specified ID
    2) A transit rule on the ingress switch that forwards traffic based on
       the specified ID
    3) An tunnel egress rule on the egress switch that decapsulates traffic
       with the specified ID and sends it to the host

    :param p4info_helper: the P4Info helper
    :param ingress_sw: the ingress switch connection
    :param egress_sw: the egress switch connection
    :param tunnel_id: the specified tunnel ID
    :param dst_eth_addr: the destination IP to match in the ingress rule
    :param dst_ip_addr: the destination Ethernet address to write in the
                        egress rule
    """
    # 1) Tunnel Ingress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.myTunnel_ingress",
        action_params={
            "dst_id": tunnel_id,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed ingress tunnel rule on %s" % ingress_sw.name)

    # 2) Tunnel Transit Rule
    # The rule will need to be added to the myTunnel_exact table and match on
    # the tunnel ID (hdr.myTunnel.dst_id). Traffic will need to be forwarded
    # using the myTunnel_forward action on the port connected to the next switch.
    #
    # For our simple topology, switch 1 and switch 2 are connected using a
    # link attached to port 2 on both switches. We have defined a variable at
    # the top of the file, switch_to_switch_port, that you can use as the output
    # port for this action.
    #
    # We will only need a transit rule on the ingress switch because we are
    # using a simple topology. In general, you'll need on transit rule for
    # each switch in the path (except the last switch, which has the egress rule),
    # and you will need to select the port dynamically for each switch based on
    # your topology.

    # TODO build the transit rule
    # TODO install the transit rule on the ingress switch
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_forward",
        action_params={
            "port": switch_to_switch_port
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed transit tunnel rule on %s" % ingress_sw.name)

    # 3) Tunnel Egress Rule
    # For our simple topology, the host will always be located on the
    # switch_to_host_port (port 1).
    # In general, you will need to keep track of which port the host is
    # connected to.
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_egress",
        action_params={
            "dstAddr": dst_eth_addr,
            "port": switch_to_host_port
        })
    egress_sw.WriteTableEntry(table_entry)
    print("Installed egress tunnel rule on %s" % egress_sw.name)


def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print('%s: ' % table_name, end=' ')
            for m in entry.match:
                print(p4info_helper.get_match_field_name(table_name, m.field_id), end=' ')
                print('%r' % (p4info_helper.get_match_field_value(m),), end=' ')
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print('->', action_name, end=' ')
            for p in action.params:
                print(p4info_helper.get_action_param_name(action_name, p.param_id), end=' ')
                print('%r' % p.value, end=' ')
            print()

def printCounter(p4info_helper, sw, counter_name, index):
    """
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    """
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print("%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            ))

def printGrpcError(e):
    print("gRPC Error:", e.details(), end=' ')
    status_code = e.code()
    print("(%s)" % status_code.name, end=' ')
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))

def SendDigestEntry(p4info_helper, sw, digest_name=None):
    digest_entry = p4info_helper.buildDigestEntry(digest_name=digest_name)
    sw.WriteDigestEntry(digest_entry)
    print("Sent DigestEntry via P4Runtime.")

def prettify(addr):
    t = tuple(int(x) for x in addr)
    return ".".join(str(x) for x in t)

def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        """s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')"""

        #f = open("logs/suspect-logs.txt", "a")

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        #s2.MasterArbitrationUpdate()

        SendDigestEntry(p4info_helper, sw=s1, digest_name="notification_digest_t")
        #SendDigestEntry(p4info_helper, sw=s2, digest_name="notification_digest_t")

        # TODO Uncomment the following two lines to read table entries from s1 and s2
        readTableRules(p4info_helper, s1)
        #readTableRules(p4info_helper, s2)

        #s2_file = open("s2_logs.csv", "w")
        #s2_file.write("distinct,absolute,variation,alarm,attack,timestamp\n")
        #s2_file = open("s2_day10.txt", "w")

        def process_digests(device):
            print(f"{device.name} start: {datetime.datetime.now()}")
            while True:
                digests = device.DigestList()
                if digests.WhichOneof('update')=='digest':    
                    for members in digests.digest.data:

                        """if members.struct.members[0].WhichOneof('data') == 'bitstring':
                            alarm_sum = int.from_bytes(members.struct.members[0].bitstring,byteorder='big')

                        if members.struct.members[1].WhichOneof('data') == 'bitstring':
                            distinct = int.from_bytes(members.struct.members[1].bitstring,byteorder='big')

                        if members.struct.members[2].WhichOneof('data') == 'bitstring':
                            absolute = int.from_bytes(members.struct.members[2].bitstring,byteorder='big')

                        if members.struct.members[3].WhichOneof('data') == 'bitstring':
                            variation = int.from_bytes(members.struct.members[3].bitstring,byteorder='big') / (2**9)"""

                        print(str(device.name))


        devices = [s1]
        threads = []

        for device in devices:
            thread = threading.Thread(target=process_digests, args=(device,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/ids.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/ids.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    main(args.p4info, args.bmv2_json)