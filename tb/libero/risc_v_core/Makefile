SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/risc_v_core

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/rv32i_top.v \
    $(PROJ_ROOT)/src/pc_unit.v \
    $(PROJ_ROOT)/src/decoder.v \
    $(PROJ_ROOT)/src/regfile.v \
    $(PROJ_ROOT)/src/alu.v

TOPLEVEL = rv32i_top
COCOTB_TEST_MODULES = test_riscv

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
