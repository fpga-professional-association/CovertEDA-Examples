SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/elevator_controller

VERILOG_SOURCES = $(PROJ_ROOT)/src/elevator_controller.v

TOPLEVEL = elevator_controller
COCOTB_TEST_MODULES = test_elevator_controller

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
