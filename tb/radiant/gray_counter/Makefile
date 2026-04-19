SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/gray_counter

VERILOG_SOURCES = $(PROJ_ROOT)/src/gray_counter.v

TOPLEVEL = gray_counter
COCOTB_TEST_MODULES = test_gray_counter

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
