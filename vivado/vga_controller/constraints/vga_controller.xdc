# =============================================================================
# XDC Constraints File for vga_controller
# Device: Xilinx Artix-7 XC7A35T-1CPG236C
# =============================================================================

create_clock -add -name pix_clk -period 39.722 -waveform {0 19.861} [get_ports clk]

set_output_delay -clock pix_clk -min -1.0 [get_ports {hsync vsync r_out[*] g_out[*] b_out[*] active}]
set_output_delay -clock pix_clk -max 2.0 [get_ports {hsync vsync r_out[*] g_out[*] b_out[*] active}]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk}]
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}]

set_false_path -from [get_ports rst_n]

# ========== Virtual-port assignments ==========
# Suppresses IOB inference — matches VIRTUAL_PIN semantics in Quartus.
set_property IO_BUFFER_TYPE NONE [get_ports {clk}]
set_property IO_BUFFER_TYPE NONE [get_ports {rst_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {hsync}]
set_property IO_BUFFER_TYPE NONE [get_ports {vsync}]
set_property IO_BUFFER_TYPE NONE [get_ports {r_out}]
set_property IO_BUFFER_TYPE NONE [get_ports {g_out}]
set_property IO_BUFFER_TYPE NONE [get_ports {b_out}]
set_property IO_BUFFER_TYPE NONE [get_ports {active}]
