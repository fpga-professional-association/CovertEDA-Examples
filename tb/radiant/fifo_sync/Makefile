SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/fifo_sync

VERILOG_SOURCES = $(PROJ_ROOT)/src/fifo_sync.v

TOPLEVEL = fifo_sync
COCOTB_TEST_MODULES = test_fifo_sync

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
