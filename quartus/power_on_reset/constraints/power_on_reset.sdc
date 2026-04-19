# Timing constraints for power_on_reset design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_input_delay -clock {clk} -max 5.000 [get_ports {delay_cfg[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {force_rst}]

set_output_delay -clock {clk} -max 5.500 [get_ports {rst_n_out}]
set_output_delay -clock {clk} -max 5.500 [get_ports {rst_done}]
set_output_delay -clock {clk} -max 5.500 [get_ports {count_out[*]}]

set_clock_uncertainty -setup 0.100 [get_clocks {clk}]
set_clock_uncertainty -hold 0.050 [get_clocks {clk}]
