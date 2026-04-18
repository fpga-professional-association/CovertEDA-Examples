SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# ws2812_top has an undriven `addr` feeding color_rom (RTL bug), so test the
# transmitter directly.
VERILOG_SOURCES := $(PWD)/../src/ws2812_tx.v
TOPLEVEL := ws2812_tx
MODULE   := test_ws2812_tx

include $(shell cocotb-config --makefiles)/Makefile.sim
