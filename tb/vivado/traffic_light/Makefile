SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/traffic_light

VERILOG_SOURCES = $(PROJ_ROOT)/src/traffic_light.v

TOPLEVEL = traffic_light
COCOTB_TEST_MODULES = test_traffic_light

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
