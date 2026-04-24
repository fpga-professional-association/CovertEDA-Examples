SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/edge_detector

VERILOG_SOURCES = $(PROJ_ROOT)/src/edge_detector.v

TOPLEVEL = edge_detector
COCOTB_TEST_MODULES = test_edge_detector

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
