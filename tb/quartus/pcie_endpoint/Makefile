SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/pcie_endpoint

VERILOG_SOURCES  = $(PROJ_ROOT)/src/pcie_top.sv
VERILOG_SOURCES += $(PROJ_ROOT)/src/tlp_handler.sv
VERILOG_SOURCES += $(PROJ_ROOT)/src/bar_decoder.sv
VERILOG_SOURCES += ../../stubs/pcie_ip_stub.v

TOPLEVEL = pcie_top
COCOTB_TEST_MODULES = test_pcie

COMPILE_ARGS += -g2012

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
