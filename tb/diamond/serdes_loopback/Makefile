SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/serdes_loopback

VERILOG_SOURCES = $(PROJ_ROOT)/src/serdes_top.v \
                  $(PROJ_ROOT)/src/serdes_wrapper.v \
                  $(PROJ_ROOT)/src/prbs_gen.v \
                  $(PROJ_ROOT)/src/prbs_check.v

TOPLEVEL = serdes_top
COCOTB_TEST_MODULES = test_serdes

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
