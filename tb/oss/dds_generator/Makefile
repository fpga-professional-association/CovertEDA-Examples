SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/dds_generator

VERILOG_SOURCES = $(PROJ_ROOT)/src/dds_generator.v

TOPLEVEL = dds_generator
COCOTB_TEST_MODULES = test_dds_generator

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
