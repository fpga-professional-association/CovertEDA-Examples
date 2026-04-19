# SPI Flash Controller - Timing Constraints
# Device: LIFCL-40-9BG400C
# Created: 2026-03-21

# Primary clock: 50 MHz
create_clock -name clk_sys -period 20.0 [get_ports clk]

# Clock uncertainty
set_clock_uncertainty -setup 1.0 [get_clocks clk_sys]

# Input delays
set_input_delay -clock clk_sys -max 3.5 [get_ports {miso rst_n}]
set_input_delay -clock clk_sys -min 1.0 [get_ports {miso rst_n}]

# Output delays
set_output_delay -clock clk_sys -max 4.5 [get_ports {sclk cs_n mosi busy}]
set_output_delay -clock clk_sys -min 1.5 [get_ports {sclk cs_n mosi busy}]

# False paths
set_false_path -from [get_ports rst_n]
