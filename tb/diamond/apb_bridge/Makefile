SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/apb_bridge

VERILOG_SOURCES = $(PROJ_ROOT)/src/apb_bridge.v

TOPLEVEL = apb_bridge
COCOTB_TEST_MODULES = test_apb_bridge

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
