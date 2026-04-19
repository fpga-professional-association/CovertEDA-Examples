SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/bus_monitor

VERILOG_SOURCES = $(PROJ_ROOT)/src/bus_monitor.v

TOPLEVEL = bus_monitor
COCOTB_TEST_MODULES = test_bus_monitor

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
