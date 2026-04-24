SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/pulse_width_measure

VERILOG_SOURCES = $(PROJ_ROOT)/src/pulse_width_measure.v

TOPLEVEL = pulse_width_measure
COCOTB_TEST_MODULES = test_pulse_width_measure

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
