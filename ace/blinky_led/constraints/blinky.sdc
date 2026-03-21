# SDC for Speedster7t Blinky

create_clock -name sys_clk -period 10.0 [get_ports clk]

set_input_delay -clock sys_clk -max 1.5 [get_ports rst_n]
set_output_delay -clock sys_clk -max 2.0 [get_ports led]

set_false_path -from [get_ports rst_n]
