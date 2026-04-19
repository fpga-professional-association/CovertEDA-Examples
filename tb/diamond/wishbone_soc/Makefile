SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/wishbone_soc

VERILOG_SOURCES = $(PROJ_ROOT)/src/soc_top.v \
                  $(PROJ_ROOT)/src/wb_sram.v \
                  $(PROJ_ROOT)/src/wb_gpio.v \
                  $(PROJ_ROOT)/src/wb_timer.v \
                  $(PROJ_ROOT)/src/wb_intercon.v

TOPLEVEL = soc_top
COCOTB_TEST_MODULES = test_soc

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
