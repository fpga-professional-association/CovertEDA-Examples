SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/glitch_filter

VERILOG_SOURCES = $(PROJ_ROOT)/src/glitch_filter.v

TOPLEVEL = glitch_filter
COCOTB_TEST_MODULES = test_glitch_filter

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
