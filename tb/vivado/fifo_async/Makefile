SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/fifo_async

VERILOG_SOURCES = $(PROJ_ROOT)/src/fifo_async.v

TOPLEVEL = fifo_async
COCOTB_TEST_MODULES = test_fifo_async

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
