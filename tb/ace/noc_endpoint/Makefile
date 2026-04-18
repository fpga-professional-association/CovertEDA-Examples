SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/noc_endpoint

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/noc_top.v \
    $(PROJ_ROOT)/src/noc_adapter.v \
    $(PROJ_ROOT)/src/packet_builder.v

TOPLEVEL = noc_top
COCOTB_TEST_MODULES = test_noc

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
