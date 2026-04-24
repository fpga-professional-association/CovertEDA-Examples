SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/pwm_multi

VERILOG_SOURCES = $(PROJ_ROOT)/src/pwm_multi.v

TOPLEVEL = pwm_multi
COCOTB_TEST_MODULES = test_pwm_multi

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
