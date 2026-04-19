SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/fft_butterfly

VERILOG_SOURCES = $(PROJ_ROOT)/src/fft_butterfly.v

TOPLEVEL = fft_butterfly
COCOTB_TEST_MODULES = test_fft_butterfly

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
