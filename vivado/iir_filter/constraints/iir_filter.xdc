# =============================================================================
# XDC Constraints File for iir_filter
# Device: Xilinx Artix-7 XC7A35T-1CPG236C
# =============================================================================

create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk]

set_input_delay -clock sys_clk -min 0.0 [get_ports {x_in[*] valid_in rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {x_in[*] valid_in rst_n}]
set_output_delay -clock sys_clk -min -1.0 [get_ports {y_out[*] valid_out}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {y_out[*] valid_out}]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk}]
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}]

set_false_path -from [get_ports rst_n]
