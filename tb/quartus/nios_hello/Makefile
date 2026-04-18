SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/nios_hello

VERILOG_SOURCES  = $(PROJ_ROOT)/src/nios_top.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/gpio_ctrl.v
VERILOG_SOURCES += $(PROJ_ROOT)/src/system_pll.v
VERILOG_SOURCES += ../../stubs/altpll_stub.v

TOPLEVEL = nios_top
COCOTB_TEST_MODULES = test_nios

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
