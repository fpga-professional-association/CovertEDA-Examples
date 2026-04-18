SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES := \
	$(PWD)/../src/spi_slave.v \
	$(PWD)/../src/reg_bank.v \
	$(PWD)/../src/spi_top.v
TOPLEVEL := spi_top
MODULE   := test_spi

include $(shell cocotb-config --makefiles)/Makefile.sim
