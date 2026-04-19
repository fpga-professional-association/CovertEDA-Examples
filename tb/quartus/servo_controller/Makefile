SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../quartus/servo_controller

VERILOG_SOURCES = $(PROJ_ROOT)/src/servo_controller.v

TOPLEVEL = servo_controller
COCOTB_TEST_MODULES = test_servo_controller

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
