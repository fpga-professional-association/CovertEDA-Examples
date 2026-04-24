# =============================================================================
# XDC Constraints File for hamming_encoder
# Device: Xilinx Artix-7 XC7A35T-1CPG236C
# =============================================================================

create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk]

set_input_delay -clock sys_clk -min 0.0 [get_ports {enc_data_in[*] enc_valid dec_data_in[*] dec_valid rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {enc_data_in[*] enc_valid dec_data_in[*] dec_valid rst_n}]
set_output_delay -clock sys_clk -min -1.0 [get_ports {enc_data_out[*] enc_done dec_data_out[*] dec_done dec_error dec_uncorrectable}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {enc_data_out[*] enc_done dec_data_out[*] dec_done dec_error dec_uncorrectable}]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk}]
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}]

set_false_path -from [get_ports rst_n]

# ========== Virtual-port assignments ==========
# Suppresses IOB inference — matches VIRTUAL_PIN semantics in Quartus.
set_property IO_BUFFER_TYPE NONE [get_ports {clk}]
set_property IO_BUFFER_TYPE NONE [get_ports {rst_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {enc_data_in}]
set_property IO_BUFFER_TYPE NONE [get_ports {enc_valid}]
set_property IO_BUFFER_TYPE NONE [get_ports {enc_data_out}]
set_property IO_BUFFER_TYPE NONE [get_ports {enc_done}]
set_property IO_BUFFER_TYPE NONE [get_ports {dec_data_in}]
set_property IO_BUFFER_TYPE NONE [get_ports {dec_valid}]
set_property IO_BUFFER_TYPE NONE [get_ports {dec_data_out}]
set_property IO_BUFFER_TYPE NONE [get_ports {dec_done}]
set_property IO_BUFFER_TYPE NONE [get_ports {dec_error}]
set_property IO_BUFFER_TYPE NONE [get_ports {dec_uncorrectable}]
