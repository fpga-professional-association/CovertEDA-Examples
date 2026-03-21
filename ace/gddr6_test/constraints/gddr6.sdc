create_clock -name gddr_clk -period 2.0 [get_ports clk]

set_input_delay -clock gddr_clk -max 0.6 [get_ports rd_data]
set_output_delay -clock gddr_clk -max 0.6 [get_ports {wr_addr wr_data wr_en rd_addr rd_en}]
