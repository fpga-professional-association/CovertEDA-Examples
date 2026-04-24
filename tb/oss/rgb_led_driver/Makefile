SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/rgb_led_driver

VERILOG_SOURCES = $(PROJ_ROOT)/src/rgb_led_driver.v

TOPLEVEL = rgb_led_driver
COCOTB_TEST_MODULES = test_rgb_led_driver

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
