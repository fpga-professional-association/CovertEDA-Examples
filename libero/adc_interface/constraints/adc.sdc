create_clock -name sys_clk -period 40.0 -waveform {0 20} [get_ports clk]
create_clock -name spi_clk -period 5.0 [get_ports adc_sclk]

set_input_delay -clock sys_clk -max 2.5 [get_ports {rst_n adc_miso}]
set_output_delay -clock sys_clk -max 3.0 [get_ports {adc_sclk adc_cs_n adc_mosi adc_data data_valid}]

set_false_path -from [get_ports rst_n]
