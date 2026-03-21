create_clock -name ml_clk -period 2.5 [get_ports clk]

set_input_delay -clock ml_clk -max 0.8 [get_ports {input_data input_valid output_ready}]
set_output_delay -clock ml_clk -max 0.8 [get_ports {output_data output_valid input_ready}]
