SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/crc_generator

VERILOG_SOURCES = $(PROJ_ROOT)/src/crc_generator.v

TOPLEVEL = crc_generator
COCOTB_TEST_MODULES = test_crc_generator

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
