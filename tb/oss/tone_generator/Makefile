SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/tone_generator

VERILOG_SOURCES = $(PROJ_ROOT)/src/tone_generator.v

TOPLEVEL = tone_generator
COCOTB_TEST_MODULES = test_tone_generator

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
