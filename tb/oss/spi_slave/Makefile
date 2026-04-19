SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/spi_slave

VERILOG_SOURCES = $(PROJ_ROOT)/src/spi_top.v \
                  $(PROJ_ROOT)/src/spi_slave.v \
                  $(PROJ_ROOT)/src/reg_bank.v

TOPLEVEL = spi_top
COCOTB_TEST_MODULES = test_spi

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
