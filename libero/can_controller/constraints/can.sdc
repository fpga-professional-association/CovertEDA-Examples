create_clock -name sys_clk -period 12.5 -waveform {0 6.25} [get_ports clk]

set_input_delay -clock sys_clk -max 2.0 [get_ports {rst_n can_rx}]
set_output_delay -clock sys_clk -max 3.0 [get_ports {can_tx rx_id rx_data rx_dlc rx_valid tx_ready}]

set_false_path -from [get_ports rst_n]
