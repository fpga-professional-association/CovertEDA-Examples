SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/priority_queue

VERILOG_SOURCES = $(PROJ_ROOT)/src/priority_queue.v

TOPLEVEL = priority_queue
COCOTB_TEST_MODULES = test_priority_queue

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
