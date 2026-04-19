SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/uart_echo

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/uart_top.sv \
    $(PROJ_ROOT)/src/uart_rx.sv \
    $(PROJ_ROOT)/src/uart_tx.sv \
    $(PROJ_ROOT)/src/sync_fifo.sv

TOPLEVEL = uart_top
COCOTB_TEST_MODULES = test_uart

COMPILE_ARGS += -g2012

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
