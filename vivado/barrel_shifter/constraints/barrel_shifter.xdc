# =============================================================================
# XDC Constraints File for barrel_shifter
# Device: Xilinx Artix-7 XC7A35T-1CPG236C
# =============================================================================

# ---- Clock Definition ----
create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk]

# ---- Input/Output Delays ----
set_input_delay -clock sys_clk -min 0.0 [get_ports {data_in[*] shift_amt[*] mode[*] valid_in rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {data_in[*] shift_amt[*] mode[*] valid_in rst_n}]
set_output_delay -clock sys_clk -min -1.0 [get_ports {data_out[*] valid_out}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {data_out[*] valid_out}]

# ---- Port Properties ----
set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk}]
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}]

# ---- Async Reset ----
set_false_path -from [get_ports rst_n]
