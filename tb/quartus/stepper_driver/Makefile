SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/stepper_driver

VERILOG_SOURCES = $(PROJ_ROOT)/src/stepper_driver.v

TOPLEVEL = stepper_driver
COCOTB_TEST_MODULES = test_stepper_driver

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
