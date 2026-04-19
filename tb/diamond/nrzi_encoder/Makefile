SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/nrzi_encoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/nrzi_encoder.v

TOPLEVEL = nrzi_encoder
COCOTB_TEST_MODULES = test_nrzi_encoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
