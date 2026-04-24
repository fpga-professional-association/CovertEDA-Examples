SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/arbiter_rr

VERILOG_SOURCES = $(PROJ_ROOT)/src/arbiter_rr.v

TOPLEVEL = arbiter_rr
COCOTB_TEST_MODULES = test_arbiter_rr

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
