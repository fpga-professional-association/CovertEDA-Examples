SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/can_controller

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/can_top.v \
    $(PROJ_ROOT)/src/can_core.v \
    $(PROJ_ROOT)/src/bit_timing.v \
    $(PROJ_ROOT)/src/msg_filter.v

TOPLEVEL = can_top
COCOTB_TEST_MODULES = test_can

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
