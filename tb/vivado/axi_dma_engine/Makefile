SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/axi_dma_engine

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/dma_top.sv \
    $(PROJ_ROOT)/src/axi_master.sv \
    $(PROJ_ROOT)/src/sg_engine.sv \
    $(PROJ_ROOT)/src/descriptor_cache.sv

TOPLEVEL = dma_top
COCOTB_TEST_MODULES = test_dma

COMPILE_ARGS += -g2012

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
