SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/leading_zeros

VERILOG_SOURCES = $(PROJ_ROOT)/src/leading_zeros.v

TOPLEVEL = leading_zeros
COCOTB_TEST_MODULES = test_leading_zeros

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
