SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../vivado/pwm_rgb

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/pwm_top.sv \
    $(PROJ_ROOT)/src/pwm_channel.sv \
    $(PROJ_ROOT)/src/axi_lite_slave.sv

TOPLEVEL = pwm_top
COCOTB_TEST_MODULES = test_pwm

COMPILE_ARGS += -g2012

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
