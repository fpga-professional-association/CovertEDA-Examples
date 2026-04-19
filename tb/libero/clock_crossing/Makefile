SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/clock_crossing

VERILOG_SOURCES = $(PROJ_ROOT)/src/clock_crossing.v

TOPLEVEL = clock_crossing
COCOTB_TEST_MODULES = test_clock_crossing

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
