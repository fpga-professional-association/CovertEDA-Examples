SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/uart_rx

VERILOG_SOURCES = $(PROJ_ROOT)/src/uart_rx.v

TOPLEVEL = uart_rx
COCOTB_TEST_MODULES = test_uart_rx

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
