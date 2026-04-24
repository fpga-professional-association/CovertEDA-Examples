SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/huffman_decoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/huffman_decoder.v

TOPLEVEL = huffman_decoder
COCOTB_TEST_MODULES = test_huffman_decoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
