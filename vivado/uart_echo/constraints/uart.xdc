# =============================================================================
# XDC Constraints for UART Echo Project
# Device: Xilinx Artix-7 XC7A100T-1CSG324C
# =============================================================================

# ---- System Clock ----
create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk]

# ---- UART Pins on Pmod JA (UART to USB) ----
# Pmod JA pin assignments (standard Digilent board)
set_property -dict { PACKAGE_PIN C17 IOSTANDARD LVCMOS33 } [get_ports {uart_rx}];  # JA1
set_property -dict { PACKAGE_PIN D18 IOSTANDARD LVCMOS33 } [get_ports {uart_tx}];  # JA2

# ---- Reset Input (active-low) ----
set_property -dict { PACKAGE_PIN N17 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}];

# ---- Status LEDs (4x LED) ----
set_property -dict { PACKAGE_PIN H17 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {status_led[0]}];  # LED0
set_property -dict { PACKAGE_PIN K15 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {status_led[1]}];  # LED1
set_property -dict { PACKAGE_PIN J13 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {status_led[2]}];  # LED2
set_property -dict { PACKAGE_PIN G17 IOSTANDARD LVCMOS33 DRIVE 12 SLEW SLOW } [get_ports {status_led[3]}];  # LED3

# ---- Timing Constraints ----

# UART is asynchronous (CDC), so these paths are false
set_false_path -from [get_ports uart_rx]
set_false_path -to [get_ports uart_tx]

# Reset is async
set_false_path -from [get_ports rst_n]

# Input/Output delays
set_input_delay -clock sys_clk -min 0.0 [get_ports {rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {rst_n}]

set_output_delay -clock sys_clk -min -1.0 [get_ports {status_led[*]}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {status_led[*]}]

# ---- Design Attributes ----
set_property ALLOW_COMBINATORIAL_LOOPS TRUE [current_design]

# ---- FIFO synchronization exception ----
# The FIFO is synchronous to sys_clk, but the clock domain crossing
# synchronizers have their own CDC constraints built in
set_false_path -from [get_clocks clk_16x_divider/clk_16x] -to [get_clocks sys_clk]
