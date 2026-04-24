# =============================================================================
# XDC Constraints File for fifo_async
# Device: Xilinx Kintex-7 XC7K325T
# =============================================================================

create_clock -add -name wr_clk -period 10.000 -waveform {0 5} [get_ports wr_clk]
create_clock -add -name rd_clk -period 12.500 -waveform {0 6.25} [get_ports rd_clk]

set_clock_groups -asynchronous -group [get_clocks wr_clk] -group [get_clocks rd_clk]

set_false_path -from [get_ports wr_rst_n]
set_false_path -from [get_ports rd_rst_n]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {wr_clk}]
set_property -dict { PACKAGE_PIN H16 IOSTANDARD LVCMOS33 } [get_ports {rd_clk}]

# ========== Virtual-port assignments ==========
# Suppresses IOB inference — matches VIRTUAL_PIN semantics in Quartus.
set_property IO_BUFFER_TYPE NONE [get_ports {wr_clk}]
set_property IO_BUFFER_TYPE NONE [get_ports {wr_rst_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {wr_data}]
set_property IO_BUFFER_TYPE NONE [get_ports {wr_en}]
set_property IO_BUFFER_TYPE NONE [get_ports {full}]
set_property IO_BUFFER_TYPE NONE [get_ports {rd_clk}]
set_property IO_BUFFER_TYPE NONE [get_ports {rd_rst_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {rd_data}]
set_property IO_BUFFER_TYPE NONE [get_ports {rd_en}]
set_property IO_BUFFER_TYPE NONE [get_ports {empty}]
