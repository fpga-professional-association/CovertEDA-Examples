SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/bit_reversal

VERILOG_SOURCES = $(PROJ_ROOT)/src/bit_reversal.v

TOPLEVEL = bit_reversal
COCOTB_TEST_MODULES = test_bit_reversal

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
