# =============================================================================
# XDC Constraints File for blinky_led
# Device: Xilinx Artix-7 XC7A35T-1CPG236C
# =============================================================================

# ---- Clock Definition ----
# 100 MHz differential clock input on LVDS (assumed clock header)
create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk_in]

# Set input delay for setup/hold analysis
set_input_delay -clock sys_clk -min 0.0 [get_ports {btn_in rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {btn_in rst_n}]

# Set output delay for LED outputs
set_output_delay -clock sys_clk -min -1.0 [get_ports {led_out[*]}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {led_out[*]}]

# ---- Port Locations (Artix-7 Evaluation Board) ----

# System Clock (100MHz from oscillator)
set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk_in}];

# Active-Low Reset (pushbutton)
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}];

# Push Buttons for mode selection
set_property -dict { PACKAGE_PIN C9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {btn_in[0]}];
set_property -dict { PACKAGE_PIN B9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {btn_in[1]}];

# LED Outputs (4 LEDs)
set_property -dict { PACKAGE_PIN H17 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {led_out[0]}];
set_property -dict { PACKAGE_PIN K15 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {led_out[1]}];
set_property -dict { PACKAGE_PIN J13 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {led_out[2]}];
set_property -dict { PACKAGE_PIN G17 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {led_out[3]}];

# ---- Timing Constraints ----

# Relax timing on button synchronizer (CDC path)
set_false_path -from [get_ports btn_in] -to [get_pins blinky_top/btn_sync_r*]

# Allow async reset
set_false_path -from [get_ports rst_n]

# ---- Design Constraints ----

# Prohibit placement in certain areas
set_property PROHIBIT TRUE [get_sites SLICE_X0Y0]
set_property PROHIBIT TRUE [get_sites SLICE_X0Y1]

# Optimize for area
set_property ALLOW_COMBINATORIAL_LOOPS TRUE [current_design]
