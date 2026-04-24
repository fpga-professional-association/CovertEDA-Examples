SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/keypad_scanner

VERILOG_SOURCES = $(PROJ_ROOT)/src/keypad_scanner.v

TOPLEVEL = keypad_scanner
COCOTB_TEST_MODULES = test_keypad_scanner

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
