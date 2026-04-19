SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/modbus_rtu

VERILOG_SOURCES = $(PROJ_ROOT)/src/modbus_rtu.v

TOPLEVEL = modbus_rtu
COCOTB_TEST_MODULES = test_modbus_rtu

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
