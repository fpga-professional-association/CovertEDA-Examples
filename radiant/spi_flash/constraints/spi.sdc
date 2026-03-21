// SPI Flash Controller - Timing Constraints
// Device: LIFCL-40-9BG400C
// Created: 2026-03-21

// Primary clock: 100 MHz
create_clock -name clk_sys -period 10.0 [get_ports clk]

// SPI clock constraint (derived, 25 MHz)
create_clock -name spi_clk -period 40.0 [get_pins spi_top/master/sclk]

// Clock uncertainty
set_clock_uncertainty -setup 1.0 -hold 0.6 [get_clocks clk_sys]

// Input delays
set_input_delay -clock clk_sys -max 3.5 [get_ports {miso rst_n}]
set_input_delay -clock clk_sys -min 1.0 [get_ports {miso rst_n}]

// Output delays
set_output_delay -clock clk_sys -max 4.5 [get_ports {sclk cs_n mosi busy}]
set_output_delay -clock clk_sys -min 1.5 [get_ports {sclk cs_n mosi busy}]

// False paths
set_false_path -from [get_ports rst_n] -to [get_clocks clk_sys]
set_false_path -from [get_clocks spi_clk] -to [get_clocks clk_sys]
