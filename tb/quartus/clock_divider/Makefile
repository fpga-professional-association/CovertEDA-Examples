SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/clock_divider

VERILOG_SOURCES = $(PROJ_ROOT)/src/clock_divider.v

TOPLEVEL = clock_divider
COCOTB_TEST_MODULES = test_clock_divider

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
