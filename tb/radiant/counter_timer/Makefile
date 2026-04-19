SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/counter_timer

VERILOG_SOURCES = $(PROJ_ROOT)/src/counter_timer.v

TOPLEVEL = counter_timer
COCOTB_TEST_MODULES = test_counter_timer

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
