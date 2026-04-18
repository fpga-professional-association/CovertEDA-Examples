SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/ethernet_mac

VERILOG_SOURCES  = $(PROJ_ROOT)/src/eth_top.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/mac_tx.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/mac_rx.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/mii_intf.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/crc32.v

TOPLEVEL = eth_top
COCOTB_TEST_MODULES = test_eth

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
