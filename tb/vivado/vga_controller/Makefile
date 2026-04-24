SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/vga_controller

VERILOG_SOURCES = $(PROJ_ROOT)/src/vga_controller.v

TOPLEVEL = vga_controller
COCOTB_TEST_MODULES = test_vga_controller

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
