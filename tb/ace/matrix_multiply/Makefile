SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/matrix_multiply

VERILOG_SOURCES = $(PROJ_ROOT)/src/matrix_multiply.v

TOPLEVEL = matrix_multiply
COCOTB_TEST_MODULES = test_matrix_multiply

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
