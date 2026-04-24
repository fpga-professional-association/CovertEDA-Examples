SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/pattern_generator

VERILOG_SOURCES = $(PROJ_ROOT)/src/pattern_generator.v

TOPLEVEL = pattern_generator
COCOTB_TEST_MODULES = test_pattern_generator

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
