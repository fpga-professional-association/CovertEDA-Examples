SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/color_space_conv

VERILOG_SOURCES = $(PROJ_ROOT)/src/color_space_conv.v

TOPLEVEL = color_space_conv
COCOTB_TEST_MODULES = test_color_space_conv

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
