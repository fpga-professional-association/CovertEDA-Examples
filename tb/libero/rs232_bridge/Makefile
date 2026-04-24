SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/rs232_bridge

VERILOG_SOURCES = $(PROJ_ROOT)/src/rs232_bridge.v

TOPLEVEL = rs232_bridge
COCOTB_TEST_MODULES = test_rs232_bridge

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
