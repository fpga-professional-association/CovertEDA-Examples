SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/ir_decoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/ir_decoder.v

TOPLEVEL = ir_decoder
COCOTB_TEST_MODULES = test_ir_decoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
