SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/i2c_master

VERILOG_SOURCES = $(PROJ_ROOT)/src/i2c_master.v

TOPLEVEL = i2c_master
COCOTB_TEST_MODULES = test_i2c_master

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
