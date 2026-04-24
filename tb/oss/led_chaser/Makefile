SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/led_chaser

VERILOG_SOURCES = $(PROJ_ROOT)/src/led_chaser.v

TOPLEVEL = led_chaser
COCOTB_TEST_MODULES = test_led_chaser

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
