SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/pdm_filter

VERILOG_SOURCES = $(PROJ_ROOT)/src/pdm_filter.v

TOPLEVEL = pdm_filter
COCOTB_TEST_MODULES = test_pdm_filter

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
