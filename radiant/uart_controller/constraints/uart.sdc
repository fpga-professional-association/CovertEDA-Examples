// UART Controller - Timing Constraints
// Device: LIFCL-40-7BG400I
// Created: 2026-03-21

// Primary clock: 50 MHz
create_clock -name clk_sys -period 20.0 [get_ports clk]

// Clock uncertainty
set_clock_uncertainty -setup 0.8 -hold 0.5 [get_clocks clk_sys]

// Input delays
set_input_delay -clock clk_sys -max 4.0 [get_ports {rx rst_n}]
set_input_delay -clock clk_sys -min 1.5 [get_ports {rx rst_n}]

// Output delays
set_output_delay -clock clk_sys -max 5.5 [get_ports {tx rx_valid tx_ready}]
set_output_delay -clock clk_sys -min 2.5 [get_ports {tx rx_valid tx_ready}]

// False path from reset
set_false_path -from [get_ports rst_n] -to [get_clocks clk_sys]

// Multi-cycle paths for baud rate divider
set_multicycle_path -setup 5 -from [get_pins {baudgen/counter[*]}]

// Baud clock domain crossing
set_false_path -from [get_clocks clk_sys] -to [get_pins {*rx*}]
set_false_path -from [get_pins {*rx*}] -to [get_clocks clk_sys]
