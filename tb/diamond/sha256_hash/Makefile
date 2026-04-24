SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PROJ_ROOT = ../../../diamond/sha256_hash

VERILOG_SOURCES = $(PROJ_ROOT)/src/sha256_hash.v

TOPLEVEL = sha256_hash
COCOTB_TEST_MODULES = test_sha256_hash

ifeq ($(OS),Windows_NT)
    export PYTHONPATH := $(shell cd ../../common && pwd);$(PYTHONPATH)
else
    export PYTHONPATH := $(shell cd ../../common && pwd):$(PYTHONPATH)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
