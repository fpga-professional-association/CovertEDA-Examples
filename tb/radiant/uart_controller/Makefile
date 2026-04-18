SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/uart_controller

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/uart_top.v \
    $(PROJ_ROOT)/src/baud_gen.v \
    $(PROJ_ROOT)/src/uart_rx.v \
    $(PROJ_ROOT)/src/uart_tx.v

TOPLEVEL = uart_top
COCOTB_TEST_MODULES = test_uart

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
