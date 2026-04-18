SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/adc_interface

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/adc_top.v \
    $(PROJ_ROOT)/src/spi_master.v \
    $(PROJ_ROOT)/src/sample_buffer.v

TOPLEVEL = adc_top
COCOTB_TEST_MODULES = test_adc

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
