// DSP FIR Filter - Timing Constraints
// Device: LIFCL-40-7BG400I
// Created: 2026-03-21

// Primary clock: 100 MHz
create_clock -name clk_sys -period 10.0 [get_ports clk]

// Clock uncertainty
set_clock_uncertainty -setup 1.0 -hold 0.6 [get_clocks clk_sys]

// Input delays
set_input_delay -clock clk_sys -max 3.0 [get_ports {data_in[*] valid_in rst_n}]
set_input_delay -clock clk_sys -min 1.0 [get_ports {data_in[*] valid_in rst_n}]

// Output delays (DSP blocks pipelined)
set_output_delay -clock clk_sys -max 4.0 [get_ports {data_out[*] valid_out}]
set_output_delay -clock clk_sys -min 2.0 [get_ports {data_out[*] valid_out}]

// False paths
set_false_path -from [get_ports rst_n] -to [get_clocks clk_sys]

// Multicycle paths through DSP blocks
set_multicycle_path -setup 2 -from [get_pins {*mac*}]
