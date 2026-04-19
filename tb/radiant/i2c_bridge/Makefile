SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/i2c_bridge

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/i2c_top.v \
    $(PROJ_ROOT)/src/i2c_slave.v \
    $(PROJ_ROOT)/src/wb_master.v

TOPLEVEL = i2c_top
COCOTB_TEST_MODULES = test_i2c

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
