# Timing constraints for spi_master design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]
set_false_path -from [get_ports {miso}]

set_input_delay -clock {clk} -max 5.000 [get_ports {data_in[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {start}]
set_input_delay -clock {clk} -max 5.000 [get_ports {cpol}]
set_input_delay -clock {clk} -max 5.000 [get_ports {cpha}]
set_input_delay -clock {clk} -max 5.000 [get_ports {clk_div[*]}]

set_output_delay -clock {clk} -max 5.500 [get_ports {data_out[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {busy}]
set_output_delay -clock {clk} -max 5.500 [get_ports {done}]
set_output_delay -clock {clk} -max 5.500 [get_ports {sck}]
set_output_delay -clock {clk} -max 5.500 [get_ports {mosi}]
set_output_delay -clock {clk} -max 5.500 [get_ports {cs_n}]

set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
set_clock_uncertainty -hold -to [get_clocks {clk}] 0.050
