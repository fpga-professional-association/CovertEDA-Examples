SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/timer_watchdog

VERILOG_SOURCES = $(PROJ_ROOT)/src/timer_watchdog.v

TOPLEVEL = timer_watchdog
COCOTB_TEST_MODULES = test_timer_watchdog

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
