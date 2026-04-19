SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/axi_width_conv

VERILOG_SOURCES = $(PROJ_ROOT)/src/axi_width_conv.v

TOPLEVEL = axi_width_conv
COCOTB_TEST_MODULES = test_axi_width_conv

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
