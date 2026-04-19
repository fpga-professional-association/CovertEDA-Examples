SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/hdlc_framer

VERILOG_SOURCES = $(PROJ_ROOT)/src/hdlc_framer.v

TOPLEVEL = hdlc_framer
COCOTB_TEST_MODULES = test_hdlc_framer

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
