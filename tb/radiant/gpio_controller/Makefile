SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../radiant/gpio_controller

VERILOG_SOURCES = $(PROJ_ROOT)/src/gpio_controller.v

TOPLEVEL = gpio_controller
COCOTB_TEST_MODULES = test_gpio_controller

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
