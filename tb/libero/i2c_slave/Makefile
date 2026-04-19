SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/i2c_slave

VERILOG_SOURCES = $(PROJ_ROOT)/src/i2c_slave.v

TOPLEVEL = i2c_slave
COCOTB_TEST_MODULES = test_i2c_slave

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
