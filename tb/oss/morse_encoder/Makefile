SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/morse_encoder

VERILOG_SOURCES = $(PROJ_ROOT)/src/morse_encoder.v

TOPLEVEL = morse_encoder
COCOTB_TEST_MODULES = test_morse_encoder

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
