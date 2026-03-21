# =============================================================================
# XDC Constraints for RGB PWM Controller
# Device: Xilinx Zynq XC7Z020-1CLG400C
# =============================================================================

# ---- System Clock (from PS) ----
create_clock -add -name ps_clk -period 20.000 -waveform {0 10} [get_ports clk]

# ---- Reset ----
set_property -dict { PACKAGE_PIN M18 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}];

# ---- RGB LED Outputs (PL side) ----
# Typically on PMOD or direct headers
set_property -dict { PACKAGE_PIN U9  IOSTANDARD LVCMOS33 DRIVE 8 SLEW FAST } [get_ports {pwm_red}];
set_property -dict { PACKAGE_PIN V9  IOSTANDARD LVCMOS33 DRIVE 8 SLEW FAST } [get_ports {pwm_green}];
set_property -dict { PACKAGE_PIN W9  IOSTANDARD LVCMOS33 DRIVE 8 SLEW FAST } [get_ports {pwm_blue}];

# ---- AXI-Lite Clock (same as PS clock) ----
# Already defined above as ps_clk

# ---- Timing Constraints ----
set_input_delay -clock ps_clk -min 0.0 [get_ports {rst_n}]
set_input_delay -clock ps_clk -max 3.0 [get_ports {rst_n}]

set_output_delay -clock ps_clk -min -1.0 [get_ports {pwm_red pwm_green pwm_blue}]
set_output_delay -clock ps_clk -max 2.0 [get_ports {pwm_red pwm_green pwm_blue}]

# ---- Design Constraints ----
set_property ALLOW_COMBINATORIAL_LOOPS TRUE [current_design]
