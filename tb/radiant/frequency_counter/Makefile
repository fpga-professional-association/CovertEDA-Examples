SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/frequency_counter

VERILOG_SOURCES = $(PROJ_ROOT)/src/frequency_counter.v

TOPLEVEL = frequency_counter
COCOTB_TEST_MODULES = test_frequency_counter

COMPILE_ARGS += -Pfrequency_counter.GATE_BITS=6

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
