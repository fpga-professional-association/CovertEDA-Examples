SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/video_scaler

VERILOG_SOURCES = $(PROJ_ROOT)/src/scaler_top.v \
                  $(PROJ_ROOT)/src/pixel_counter.v \
                  $(PROJ_ROOT)/src/line_buffer.v \
                  $(PROJ_ROOT)/src/interpolator.v

TOPLEVEL = scaler_top
COCOTB_TEST_MODULES = test_scaler

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
