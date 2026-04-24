# Gray Counter - Timing Constraints
# Device: LIFCL-40-7BG400I

create_clock -name clk_sys -period 40.0 [get_ports clk]
set_clock_uncertainty -setup 0.5 [get_clocks clk_sys]

set_input_delay -clock clk_sys -max 3.5 [get_ports enable]
set_input_delay -clock clk_sys -min 1.5 [get_ports enable]

set_output_delay -clock clk_sys -max 5.0 [get_ports {gray_out[*]}]
set_output_delay -clock clk_sys -min 2.0 [get_ports {gray_out[*]}]
set_output_delay -clock clk_sys -max 5.0 [get_ports {binary_out[*]}]
set_output_delay -clock clk_sys -min 2.0 [get_ports {binary_out[*]}]

set_false_path -from [get_ports rst_n]
