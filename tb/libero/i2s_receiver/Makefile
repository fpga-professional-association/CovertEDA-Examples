SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/i2s_receiver

VERILOG_SOURCES = $(PROJ_ROOT)/src/i2s_receiver.v

TOPLEVEL = i2s_receiver
COCOTB_TEST_MODULES = test_i2s_receiver

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
