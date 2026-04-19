# =============================================================================
# XDC Constraints File for dpram
# Device: Xilinx Artix-7 XC7A200T
# =============================================================================

create_clock -add -name clk_a -period 10.000 -waveform {0 5} [get_ports clk_a]
create_clock -add -name clk_b -period 10.000 -waveform {0 5} [get_ports clk_b]

set_input_delay -clock clk_a -min 0.0 [get_ports {addr_a[*] din_a[*] en_a we_a}]
set_input_delay -clock clk_a -max 3.0 [get_ports {addr_a[*] din_a[*] en_a we_a}]
set_input_delay -clock clk_b -min 0.0 [get_ports {addr_b[*] din_b[*] en_b we_b}]
set_input_delay -clock clk_b -max 3.0 [get_ports {addr_b[*] din_b[*] en_b we_b}]

set_output_delay -clock clk_a -min -1.0 [get_ports {dout_a[*]}]
set_output_delay -clock clk_a -max 2.0 [get_ports {dout_a[*]}]
set_output_delay -clock clk_b -min -1.0 [get_ports {dout_b[*]}]
set_output_delay -clock clk_b -max 2.0 [get_ports {dout_b[*]}]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk_a}]
set_property -dict { PACKAGE_PIN H16 IOSTANDARD LVCMOS33 } [get_ports {clk_b}]
