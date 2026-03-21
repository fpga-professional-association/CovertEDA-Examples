// Blinky LED Design - Timing and Delay Constraints
// Device: LIFCL-40-7BG400I
// Created: 2026-03-21

// Clock definitions
create_clock -name clk_sys -period 40.0 [get_ports clk]

// Clock propagation uncertainty (typical for LIFCL-40)
set_clock_uncertainty -setup 0.5 -hold 0.3 [get_clocks clk_sys]

// Input delay constraints (external clock to input)
set_input_delay -clock clk_sys -max 3.5 [get_ports rst_n]
set_input_delay -clock clk_sys -min 1.5 [get_ports rst_n]

// Output delay constraints (output propagation)
set_output_delay -clock clk_sys -max 5.0 [get_ports {led[*]}]
set_output_delay -clock clk_sys -min 2.0 [get_ports {led[*]}]

// False path constraints (reset is asynchronous)
set_false_path -from [get_ports rst_n] -to [get_clocks clk_sys]

// Multicycle paths
set_multicycle_path -setup 2 -from [get_pins {counter[*]}]
