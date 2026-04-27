# =============================================================================
# XDC Constraints File for timer_watchdog
# Device: Xilinx Artix-7 XC7A35T-1CPG236C
# =============================================================================

create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk]

set_input_delay -clock sys_clk -min 0.0 [get_ports {timeout_val[*] kick enable rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {timeout_val[*] kick enable rst_n}]
set_output_delay -clock sys_clk -min -1.0 [get_ports {wdt_reset wdt_warning counter[*]}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {wdt_reset wdt_warning counter[*]}]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk}]
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}]

set_false_path -from [get_ports rst_n]

# ========== Virtual-port assignments ==========
# Suppresses IOB inference — matches VIRTUAL_PIN semantics in Quartus.
set_property IO_BUFFER_TYPE NONE [get_ports {clk}]
set_property IO_BUFFER_TYPE NONE [get_ports {rst_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {timeout_val}]
set_property IO_BUFFER_TYPE NONE [get_ports {kick}]
set_property IO_BUFFER_TYPE NONE [get_ports {enable}]
set_property IO_BUFFER_TYPE NONE [get_ports {wdt_reset}]
set_property IO_BUFFER_TYPE NONE [get_ports {wdt_warning}]
set_property IO_BUFFER_TYPE NONE [get_ports {counter}]
