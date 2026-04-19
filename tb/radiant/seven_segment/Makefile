SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/seven_segment

VERILOG_SOURCES = $(PROJ_ROOT)/src/seven_segment.v

TOPLEVEL = seven_segment
COCOTB_TEST_MODULES = test_seven_segment

COMPILE_ARGS += -Pseven_segment.REFRESH_BITS=4

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
