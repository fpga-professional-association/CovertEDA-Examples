# SDC for Speedster7t AXI Interconnect

create_clock -name sys_clk -period 10.0 [get_ports clk]

set_input_delay -clock sys_clk -max 1.5 [get_ports rst_n]
set_false_path -from [get_ports rst_n]
