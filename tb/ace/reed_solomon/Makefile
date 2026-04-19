SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/reed_solomon

VERILOG_SOURCES = $(PROJ_ROOT)/src/reed_solomon.v

TOPLEVEL = reed_solomon
COCOTB_TEST_MODULES = test_reed_solomon

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
