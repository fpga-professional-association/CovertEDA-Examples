create_clock -name eth_clk -period 3.1 [get_ports clk_ref]

set_input_delay -clock eth_clk -max 1.0 [get_ports {tx_data tx_valid}]
set_output_delay -clock eth_clk -max 1.0 [get_ports {rx_data rx_valid tx_ready}]
