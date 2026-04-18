SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/ws2812_driver

VERILOG_SOURCES = $(PROJ_ROOT)/src/ws2812_top.v \
                  $(PROJ_ROOT)/src/ws2812_tx.v \
                  $(PROJ_ROOT)/src/color_rom.v \
                  $(PROJ_ROOT)/src/gamma_lut.v

TOPLEVEL = ws2812_top
COCOTB_TEST_MODULES = test_ws2812

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
