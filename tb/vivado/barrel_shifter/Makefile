SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/barrel_shifter

VERILOG_SOURCES = $(PROJ_ROOT)/src/barrel_shifter.v

TOPLEVEL = barrel_shifter
COCOTB_TEST_MODULES = test_barrel_shifter

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
