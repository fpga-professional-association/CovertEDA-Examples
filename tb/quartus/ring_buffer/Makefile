SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/ring_buffer

VERILOG_SOURCES = $(PROJ_ROOT)/src/ring_buffer.v

TOPLEVEL = ring_buffer
COCOTB_TEST_MODULES = test_ring_buffer

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
