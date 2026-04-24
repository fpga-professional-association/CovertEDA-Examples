SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/ps2_keyboard

VERILOG_SOURCES = $(PROJ_ROOT)/src/ps2_keyboard.v

TOPLEVEL = ps2_keyboard
COCOTB_TEST_MODULES = test_ps2_keyboard

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
