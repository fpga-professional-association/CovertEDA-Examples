SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/ml_accelerator

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/ml_top.sv \
    $(PROJ_ROOT)/src/mac_array.sv \
    $(PROJ_ROOT)/src/activation.sv \
    $(PROJ_ROOT)/src/weight_buffer.sv

TOPLEVEL = ml_top
COCOTB_TEST_MODULES = test_ml

COMPILE_ARGS += -g2012

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
