SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/axi_interconnect

VERILOG_SOURCES = $(PROJ_ROOT)/src/axi_interconnect.v

TOPLEVEL = axi_interconnect
COCOTB_TEST_MODULES = test_axi_interconnect

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
