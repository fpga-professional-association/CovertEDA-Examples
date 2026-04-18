SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/signal_proc

VERILOG_SOURCES  = $(PROJ_ROOT)/src/ddc_top.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/nco.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/cic_filter.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/fir_decimate.v

TOPLEVEL = ddc_top
COCOTB_TEST_MODULES = test_ddc

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
