SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/blinky_led

VERILOG_SOURCES = $(PROJ_ROOT)/src/blinky_top.v

TOPLEVEL = blinky_top
COCOTB_TEST_MODULES = test_blinky

COMPILE_ARGS += -Pblinky_top.COUNT_MAX=10

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
