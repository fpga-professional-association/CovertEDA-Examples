SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/power_on_reset

VERILOG_SOURCES = $(PROJ_ROOT)/src/power_on_reset.v

TOPLEVEL = power_on_reset
COCOTB_TEST_MODULES = test_power_on_reset

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
