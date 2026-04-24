SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/priority_encoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/priority_encoder.v

TOPLEVEL = priority_encoder
COCOTB_TEST_MODULES = test_priority_encoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
