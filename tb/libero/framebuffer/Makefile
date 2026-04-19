SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/framebuffer

VERILOG_SOURCES = $(PROJ_ROOT)/src/framebuffer.v

TOPLEVEL = framebuffer
COCOTB_TEST_MODULES = test_framebuffer

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
