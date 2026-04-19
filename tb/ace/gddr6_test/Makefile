SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/gddr6_test

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/gddr6_top.v \
    $(PROJ_ROOT)/src/traffic_gen.v \
    $(PROJ_ROOT)/src/data_checker.v

TOPLEVEL = gddr6_top
COCOTB_TEST_MODULES = test_gddr6

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
