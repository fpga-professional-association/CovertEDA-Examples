SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/uart_bridge

VERILOG_SOURCES = $(PROJ_ROOT)/src/uart_top.v \
                  $(PROJ_ROOT)/src/uart_core.v \
                  $(PROJ_ROOT)/src/fifo_sync.v

TOPLEVEL = uart_top
COCOTB_TEST_MODULES = test_uart

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
