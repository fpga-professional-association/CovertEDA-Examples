SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/dsp_fir_filter

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/fir_top.v \
    $(PROJ_ROOT)/src/fir_mac.v \
    $(PROJ_ROOT)/src/coeff_rom.v

TOPLEVEL = fir_top
COCOTB_TEST_MODULES = test_fir

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
