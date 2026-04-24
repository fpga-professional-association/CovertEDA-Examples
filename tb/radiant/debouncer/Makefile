SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/debouncer

VERILOG_SOURCES = $(PROJ_ROOT)/src/debouncer.v

TOPLEVEL = debouncer
COCOTB_TEST_MODULES = test_debouncer

COMPILE_ARGS += -Pdebouncer.DEBOUNCE_BITS=4

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
