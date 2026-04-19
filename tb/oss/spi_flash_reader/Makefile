SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/spi_flash_reader

VERILOG_SOURCES = $(PROJ_ROOT)/src/spi_flash_reader.v

TOPLEVEL = spi_flash_reader
COCOTB_TEST_MODULES = test_spi_flash_reader

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
