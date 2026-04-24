SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../ace/rate_limiter

VERILOG_SOURCES = $(PROJ_ROOT)/src/rate_limiter.v

TOPLEVEL = rate_limiter
COCOTB_TEST_MODULES = test_rate_limiter

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
