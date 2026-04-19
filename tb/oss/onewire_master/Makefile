SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/onewire_master

VERILOG_SOURCES = $(PROJ_ROOT)/src/onewire_master.v

TOPLEVEL = onewire_master
COCOTB_TEST_MODULES = test_onewire_master

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
