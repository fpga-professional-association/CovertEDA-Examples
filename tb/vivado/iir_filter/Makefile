SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/iir_filter

VERILOG_SOURCES = $(PROJ_ROOT)/src/iir_filter.v

TOPLEVEL = iir_filter
COCOTB_TEST_MODULES = test_iir_filter

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
