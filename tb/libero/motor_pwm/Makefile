SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../libero/motor_pwm

VERILOG_SOURCES = \
    $(PROJ_ROOT)/src/motor_top.v \
    $(PROJ_ROOT)/src/pwm_gen.v \
    $(PROJ_ROOT)/src/dead_time.v \
    $(PROJ_ROOT)/src/encoder_intf.v

TOPLEVEL = motor_top
COCOTB_TEST_MODULES = test_motor

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
