SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/rom_lookup

VERILOG_SOURCES = $(PROJ_ROOT)/src/rom_lookup.v

TOPLEVEL = rom_lookup
COCOTB_TEST_MODULES = test_rom_lookup

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
