# Timing constraints for bus_monitor design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]

set_input_delay -clock {clk} -max 5.000 [get_ports {bus_valid}]
set_input_delay -clock {clk} -max 5.000 [get_ports {bus_ready}]
set_input_delay -clock {clk} -max 5.000 [get_ports {bus_wr}]
set_input_delay -clock {clk} -max 5.000 [get_ports {bus_addr[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {bus_data[*]}]

set_output_delay -clock {clk} -max 5.500 [get_ports {total_count[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {wr_count[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {rd_count[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {last_addr[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {last_data[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {bus_active}]

set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
set_clock_uncertainty -hold -to [get_clocks {clk}] 0.050
