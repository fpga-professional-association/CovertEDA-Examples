SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/manchester_encoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/manchester_encoder.v

TOPLEVEL = manchester_encoder
COCOTB_TEST_MODULES = test_manchester_encoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
