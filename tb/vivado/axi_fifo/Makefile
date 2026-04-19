SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/axi_fifo

VERILOG_SOURCES = $(PROJ_ROOT)/src/axi_fifo.v

TOPLEVEL = axi_fifo
COCOTB_TEST_MODULES = test_axi_fifo

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
