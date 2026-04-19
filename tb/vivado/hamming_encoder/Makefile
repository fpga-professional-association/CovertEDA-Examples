SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/hamming_encoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/hamming_encoder.v

TOPLEVEL = hamming_encoder
COCOTB_TEST_MODULES = test_hamming_encoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
