SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/checksum

VERILOG_SOURCES = $(PROJ_ROOT)/src/checksum.v

TOPLEVEL = checksum
COCOTB_TEST_MODULES = test_checksum

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
