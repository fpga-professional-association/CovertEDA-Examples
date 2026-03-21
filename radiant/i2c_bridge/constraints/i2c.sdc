// I2C Bridge - Timing Constraints
// Device: LFD2NX-40-7MG672
// Created: 2026-03-21

// Primary clock: 50 MHz
create_clock -name clk_sys -period 20.0 [get_ports clk]

// Clock uncertainty
set_clock_uncertainty -setup 0.8 -hold 0.5 [get_clocks clk_sys]

// I2C timing (slow bus, no tight constraints needed)
set_input_delay -clock clk_sys -max 5.0 [get_ports {sda scl rst_n}]
set_input_delay -clock clk_sys -min 2.0 [get_ports {sda scl rst_n}]

// Output delays
set_output_delay -clock clk_sys -max 6.0 [get_ports {sda scl}]
set_output_delay -clock clk_sys -min 2.5 [get_ports {sda scl}]

// False paths
set_false_path -from [get_ports rst_n] -to [get_clocks clk_sys]

// I2C is asynchronous (slow clock stretching)
set_false_path -from [get_ports sda] -to [get_clocks clk_sys]
set_false_path -from [get_ports scl] -to [get_clocks clk_sys]
