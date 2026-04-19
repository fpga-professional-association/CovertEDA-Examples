SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/sigma_delta_dac

VERILOG_SOURCES = $(PROJ_ROOT)/src/sigma_delta_dac.v

TOPLEVEL = sigma_delta_dac
COCOTB_TEST_MODULES = test_sigma_delta_dac

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
