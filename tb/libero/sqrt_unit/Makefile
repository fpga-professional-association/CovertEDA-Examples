SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/sqrt_unit

VERILOG_SOURCES = $(PROJ_ROOT)/src/sqrt_unit.v

TOPLEVEL = sqrt_unit
COCOTB_TEST_MODULES = test_sqrt_unit

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
