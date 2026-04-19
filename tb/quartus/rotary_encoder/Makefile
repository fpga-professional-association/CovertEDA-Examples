SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/rotary_encoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/rotary_encoder.v

TOPLEVEL = rotary_encoder
COCOTB_TEST_MODULES = test_rotary_encoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
