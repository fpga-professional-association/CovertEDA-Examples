SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../oss/pwm_audio

VERILOG_SOURCES = $(PROJ_ROOT)/src/audio_top.v \
                  $(PROJ_ROOT)/src/pwm_dac.v \
                  $(PROJ_ROOT)/src/sample_rom.v

TOPLEVEL = audio_top
COCOTB_TEST_MODULES = test_audio

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
