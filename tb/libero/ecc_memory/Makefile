SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/ecc_memory

VERILOG_SOURCES = $(PROJ_ROOT)/src/ecc_memory.v

TOPLEVEL = ecc_memory
COCOTB_TEST_MODULES = test_ecc_memory

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
