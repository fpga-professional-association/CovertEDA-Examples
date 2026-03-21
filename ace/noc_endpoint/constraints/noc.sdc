create_clock -name noc_clk -period 2.0 [get_ports clk]

set_input_delay -clock noc_clk -max 0.8 [get_ports {noc_in_data noc_in_valid}]
set_output_delay -clock noc_clk -max 0.8 [get_ports {noc_out_data noc_out_valid}]
