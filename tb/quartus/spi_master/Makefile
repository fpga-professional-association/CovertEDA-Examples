SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/spi_master

VERILOG_SOURCES = $(PROJ_ROOT)/src/spi_master.v

TOPLEVEL = spi_master
COCOTB_TEST_MODULES = test_spi_master

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
