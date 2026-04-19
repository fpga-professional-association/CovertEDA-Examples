SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/cache_direct

VERILOG_SOURCES = $(PROJ_ROOT)/src/cache_direct.v

TOPLEVEL = cache_direct
COCOTB_TEST_MODULES = test_cache_direct

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
