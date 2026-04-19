SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/interrupt_controller

VERILOG_SOURCES = $(PROJ_ROOT)/src/interrupt_controller.v

TOPLEVEL = interrupt_controller
COCOTB_TEST_MODULES = test_interrupt_controller

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
