SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/i2s_transmitter

VERILOG_SOURCES = $(PROJ_ROOT)/src/i2s_transmitter.v

TOPLEVEL = i2s_transmitter
COCOTB_TEST_MODULES = test_i2s_transmitter

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
