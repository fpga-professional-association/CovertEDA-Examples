SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/convolution_engine

VERILOG_SOURCES = $(PROJ_ROOT)/src/convolution_engine.v

TOPLEVEL = convolution_engine
COCOTB_TEST_MODULES = test_convolution_engine

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
