SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/ethernet_400g

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/eth400g_top.sv \
    $(PROJ_ROOT)/src/mac_engine.sv \
    $(PROJ_ROOT)/src/pcs_layer.sv

TOPLEVEL = eth400g_top
COCOTB_TEST_MODULES = test_eth400g

COMPILE_ARGS += -g2012

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
