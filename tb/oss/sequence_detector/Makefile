SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/sequence_detector

VERILOG_SOURCES = $(PROJ_ROOT)/src/sequence_detector.v

TOPLEVEL = sequence_detector
COCOTB_TEST_MODULES = test_sequence_detector

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
