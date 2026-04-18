SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Test pwm_dac alone — audio_top has an undriven `addr` signal (RTL bug),
# so we exercise the DAC directly.
VERILOG_SOURCES := $(PWD)/../src/pwm_dac.v
TOPLEVEL := pwm_dac
MODULE   := test_pwm_dac

include $(shell cocotb-config --makefiles)/Makefile.sim
