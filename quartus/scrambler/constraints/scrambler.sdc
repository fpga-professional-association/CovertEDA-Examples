# Timing constraints for scrambler design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]

set_input_delay -clock {clk} -max 5.000 [get_ports {din[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {key[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {valid_in}]
set_input_delay -clock {clk} -max 5.000 [get_ports {descramble}]

set_output_delay -clock {clk} -max 5.500 [get_ports {dout[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {valid_out}]

set_clock_uncertainty -setup 0.100 [get_clocks {clk}]
set_clock_uncertainty -hold 0.050 [get_clocks {clk}]
