SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/dma_controller

VERILOG_SOURCES = $(PROJ_ROOT)/src/dma_controller.v

TOPLEVEL = dma_controller
COCOTB_TEST_MODULES = test_dma_controller

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
