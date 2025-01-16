# /opt/netronome/p4/bin/nfp4build --output-nffw-filename ./build/program.nffw --pif-output-dir ./pifs --sku AMDA0096-0001:0 --platform lithium --block-make --nfp4c_p4_version 16 --nfp4c_p4_compiler p4c-nfp --nfirc_mac_ingress_timestamp --nfirc_multicast_group_count 16 --nfirc_multicast_group_size 16  --define PIF_PLUGIN_INIT --sandbox-c src/pif_plugin.c --reduced-thread-usage --shared-codestore --nfirc_all_header_ops --nfirc_no_implicit_header_valid --nfirc_zero_new_headers --incl-p4-build src/main.p4

REMOTEHOST=<remote-host>
CONFIG=configs/config.json

.PHONY: default
default:
	$(MAKE) -f Makefile-nfp4build 
	./utils/fix-cache-bypass.sh	
	$(MAKE) -f Makefile-nfp4build 

.PHONY: load
load:
	$(MAKE) -f Makefile-nfp4build load REMOTEHOST=$(REMOTEHOST) CONFIG=$(CONFIG) 
  
.PHONY: clean
clean:
	$(MAKE) -f Makefile-nfp4build clean
