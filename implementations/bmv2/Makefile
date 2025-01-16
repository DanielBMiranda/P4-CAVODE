# SPDX-License-Identifier: Apache-2.0

PROJECT = ids
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = topology/topology.json
SOURCE_DIR = src
BUILD_DIR = build
PCAP_DIR = pcaps
LOG_DIR = logs
RULES_SCRIPT = topology/controller/controller.py

P4C = p4c-bm2-ss
P4C_ARGS += --p4runtime-files $(BUILD_DIR)/$(PROJECT).p4.p4info.txt

RUN_SCRIPT = utils/run_exercise.py

ifndef TOPO
TOPO = topology.json
endif

source = $(SOURCE_DIR)/$(PROJECT).p4
compiled_json := $(source:.p4=.json)

DEFAULT_PROG = $(PROJECT).p4
DEFAULT_JSON = $(BUILD_DIR)/$(DEFAULT_PROG:.p4=.json)

# Define NO_P4 to start BMv2 without a program
ifndef NO_P4
run_args += -j $(DEFAULT_JSON)
endif

# Set BMV2_SWITCH_EXE to override the BMv2 target
ifdef BMV2_SWITCH_EXE
run_args += -b $(BMV2_SWITCH_EXE)
endif

all: clean 
	make run

run: build
	xterm -hold -e sudo python3 $(RUN_SCRIPT) -t $(TOPO) $(run_args) & xterm -hold -e 'sleep 7; ./$(RULES_SCRIPT)'

stop:
	sudo mn -c

build: dirs $(compiled_json)

%.json: %.p4
	$(P4C) --p4v 16 $(P4C_ARGS) -o $(BUILD_DIR)/$(PROJECT).json $<

dirs:
	mkdir -p $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)

clean: stop
	rm -f pcaps/*.pcap
	rm -rf $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)