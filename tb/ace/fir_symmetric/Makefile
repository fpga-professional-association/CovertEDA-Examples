SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/fir_symmetric

VERILOG_SOURCES = $(PROJ_ROOT)/src/fir_symmetric.v

TOPLEVEL = fir_symmetric
COCOTB_TEST_MODULES = test_fir_symmetric

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
