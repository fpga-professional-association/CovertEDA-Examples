SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/temp_sensor_spi

VERILOG_SOURCES = $(PROJ_ROOT)/src/temp_sensor_spi.v

TOPLEVEL = temp_sensor_spi
COCOTB_TEST_MODULES = test_temp_sensor_spi

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
