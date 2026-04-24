SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/logic_analyzer

VERILOG_SOURCES = $(PROJ_ROOT)/src/logic_analyzer.v

TOPLEVEL = logic_analyzer
COCOTB_TEST_MODULES = test_logic_analyzer

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
