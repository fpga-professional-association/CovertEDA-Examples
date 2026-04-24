SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/phase_detector

VERILOG_SOURCES = $(PROJ_ROOT)/src/phase_detector.v

TOPLEVEL = phase_detector
COCOTB_TEST_MODULES = test_phase_detector

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
