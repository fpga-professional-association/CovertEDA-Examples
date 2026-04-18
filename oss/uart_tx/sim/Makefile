SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES := \
	$(PWD)/../src/baud_gen.v \
	$(PWD)/../src/uart_tx.v \
	$(PWD)/../src/uart_top.v
TOPLEVEL := uart_top
MODULE   := test_uart

include $(shell cocotb-config --makefiles)/Makefile.sim
