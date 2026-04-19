SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/aes_encrypt

VERILOG_SOURCES = $(PROJ_ROOT)/src/aes_encrypt.v

TOPLEVEL = aes_encrypt
COCOTB_TEST_MODULES = test_aes_encrypt

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
