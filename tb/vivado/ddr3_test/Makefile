SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/ddr3_test

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/mem_top.v \
    $(PROJ_ROOT)/src/traffic_gen.v \
    $(PROJ_ROOT)/src/pattern_checker.v

TOPLEVEL = mem_top
COCOTB_TEST_MODULES = test_ddr3

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
